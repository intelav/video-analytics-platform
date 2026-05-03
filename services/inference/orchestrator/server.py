import grpc
from concurrent import futures
import multimodal_pb2
import multimodal_pb2_grpc

from vlm_client import VLMClient
from llm_client import LLMClient
from asr import ASR
from tts import TTS
from utils import decode_image, save_audio_temp


class MultiModalServicer(multimodal_pb2_grpc.MultiModalServiceServicer):

    def __init__(self):
        self.vlm = VLMClient()
        self.llm = LLMClient()
        self.asr = ASR()
        self.tts = TTS()

    def ProcessFrame(self, request, context):
        image = decode_image(request.image)
        prompt = request.prompt

        # Step 1: VLM
        vlm_result = self.vlm.infer(image, prompt)

        # Step 2: LLM reasoning
        final_text = self.llm.generate(
            f"User asked: {prompt}\nVision output: {vlm_result}"
        )

        # Step 3: TTS
        audio = self.tts.speak(final_text)

        return multimodal_pb2.Response(
            text=final_text,
            audio=audio
        )

    def ProcessVoice(self, request, context):
        audio_path = save_audio_temp(request.audio)

        # Step 1: ASR
        text = self.asr.transcribe(audio_path)

        # Step 2: LLM
        response = self.llm.generate(text)

        # Step 3: TTS
        audio = self.tts.speak(response)

        return multimodal_pb2.Response(
            text=response,
            audio=audio
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    multimodal_pb2_grpc.add_MultiModalServiceServicer_to_server(
        MultiModalServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("🚀 gRPC Server running on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()