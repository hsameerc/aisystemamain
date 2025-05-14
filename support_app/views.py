import os
import subprocess
import json
import openai
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SupportTrainingData, SupportModel
from .serializers import SupportDataSerializer, SupportModelSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.exceptions import ValidationError

import logging
from openai import OpenAI

logger = logging.getLogger(__name__)
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key
client = OpenAI(
    api_key=api_key  # os.environ.get("OPENAI_API_KEY"),
)


# SupportModel views
class SupportModelListCreateAPIView(generics.ListCreateAPIView):
    queryset = SupportModel.objects.all()
    serializer_class = SupportModelSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return SupportModel.objects.filter(user=user)


class SupportModelRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SupportModel.objects.all()
    serializer_class = SupportModelSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)


# Support Data views
class SupportDataListCreateAPIView(generics.ListCreateAPIView):
    queryset = SupportTrainingData.objects.all()
    serializer_class = SupportDataSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        kwargs = self.kwargs
        support_model_id = kwargs.get('support_model_id')
        try:
            support_model = SupportModel.objects.get(id=support_model_id)
            return SupportTrainingData.objects.filter(support_model=support_model)
        except SupportModel.DoesNotExist:
            raise ValidationError("SupportModel not found or does not belong to the current user.")


class SupportDataRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SupportTrainingData.objects.all()
    serializer_class = SupportDataSerializer
    permission_classes = (IsAuthenticated,)


class SupportModelValidateAPIView(RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        support_model_instance = get_object_or_404(SupportModel, id=self.kwargs['pk'])
        support_training_data = SupportTrainingData.objects.filter(support_model=support_model_instance)
        data_list = []
        for support_data in support_training_data:
            formatted_data = {
                "prompt": support_data.prompt,
                "completion": " " + support_data.completion
            }
            data_list.append(formatted_data)

        folder_path = "temp/"
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, str(support_model_instance.id) + '.jsonl')
        with open(file_path, 'w') as json_file:
            for item in data_list:
                json.dump(item, json_file)
                json_file.write('\n')

        openai_command = f"openai tools fine_tunes.prepare_data -f {file_path}"
        try:
            result = subprocess.run(openai_command, shell=True, capture_output=True, text=True)
            output = result.stdout
            logger.debug("Validation Complete.")
            message = 'Validation Complete.'
        except subprocess.CalledProcessError as e:
            output = ''
            message = f"Error executing command: {e}"

        response_data = {
            'support_model_id': support_model_instance.id,
            'file_path': file_path,
            'output': {
                'output': output,
                'message': message,
            }
        }
        return Response(response_data)


class SupportModelCompletionAPIView(RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        prompt = request.GET.get('prompt')
        conversation_id = request.GET.get('conversation_id')

        if conversation_id:
            pass
            # TODO:: Store conversation and Store and submit

        support_model_instance = get_object_or_404(SupportModel, id=self.kwargs['pk'])

        engine = support_model_instance.engine
        model_type = support_model_instance.model_type
        model_response_type = support_model_instance.response_type
        completion_messages = support_model_instance.support_training_data.all()
        try:
            if model_type != 'fine-tune':
                response_format = {}
                if model_response_type == 'json':
                    response_format = {"type": "json_object"}
                messages = []
                for c_messages in completion_messages:
                    messages.append({"role": c_messages.prompt, "content": c_messages.completion})
                messages.append({"role": "user", "content": prompt})
                response = client.chat.completions.create(
                    model=str(engine),
                    response_format=response_format,
                    messages=messages,
                    max_tokens=150,
                    n=1,
                    stop=None,
                    temperature=0.7
                )
            else:
                response = client.chat.completions.create(

                )
            message = response.choices[0].message
            response_data = {
                'prompt': prompt,
                'response': message,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except openai.OpenAIError as e:
            error_message = f"OpenAI Error: {e}"
            response_data = {
                'prompt': prompt,
                'response': error_message,
            }
            return Response(response_data, status=status.HTTP_424_FAILED_DEPENDENCY)
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            response_data = {
                'prompt': prompt,
                'response': error_message,
            }
            return Response(response_data, status=status.HTTP_424_FAILED_DEPENDENCY)


class SupportModelFineTuneAPIView(RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        support_model_instance = get_object_or_404(SupportModel, id=self.kwargs['pk'])
        engine = "gpt-3.5-turbo"  ## support_model_instance.engine
        model_name = support_model_instance.id
        folder_path = "temp/"
        file_path = os.path.join(folder_path, str(support_model_instance.id) + '.jsonl')
        if os.path.exists(folder_path):
            training_file = open(file_path, "rb")
            try:
                files_output = client.files.create(
                    file=training_file,
                    purpose="fine-tune"
                )
                output = client.fine_tuning.jobs.create(
                    training_file=files_output.id,
                    model=engine,
                    suffix=model_name
                )
                # output = client.fine_tuning.jobs.list()
                # client.fine_tuning.jobs.cancel(support_model_instance.id)
                # client.fine_tuning.jobs.list_events(
                #     fine_tuning_job_id=support_model_instance.id,
                #     limit=2
                # )
                # client.fine_tuning.jobs.retrieve(support_model_instance.id)
                #
                # client.chat.completions.create(
                #     messages=[
                #         {
                #             "role": "user",
                #             "content": "Say this is a test",
                #         }
                #     ],
                #     model="gpt-3.5-turbo",
                # )
                # client = OpenAI()
                # client.api_key = api_key
                # output = client.fine_tuning.jobs.create(
                #     training_file=file_path,
                #     model="gpt-3.5-turbo",
                #     suffix=model_name
                # )

                ### Files

                # client.files.list()

                output = output
                message = 'Fine Tune Complete.'
                logger.debug(output)
                # TODO:: update support_modal tuned_at
                support_model_instance.finetune = output
                support_model_instance.preparation = files_output
                support_model_instance.save()
                # if support_model_serializer.is_valid():
                #     support_model_serializer.save()
            except subprocess.CalledProcessError as e:
                output = ''
                message = f"Error executing command: {e}"

            response_data = {
                'support_model_id': support_model_instance.id,
                'output': {
                    'output': output,
                    'message': message,
                }
            }
            return Response(response_data)
        else:
            return Response({
                'support_model_id': support_model_instance.id,
                "message": "Please Validate Model First. Fine Tune file is not created yet!"
            }, status=400)
