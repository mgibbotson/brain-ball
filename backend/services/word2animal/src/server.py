"""
Word2Animal gRPC server. Exposes GetAnimal (stub returning default animal).
Health: HTTP /health on a separate port for readiness probing.
"""
import logging
import os
import threading
import time
from concurrent import futures

import grpc
from http.server import HTTPServer, BaseHTTPRequestHandler

import word2animal_pb2
import word2animal_pb2_grpc

import inference

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s level=%(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

GRPC_PORT = int(os.environ.get("GRPC_PORT", "50051"))
HEALTH_PORT = int(os.environ.get("HEALTH_PORT", "50052"))


class Word2AnimalServicer(word2animal_pb2_grpc.Word2AnimalServicer):
    """Calls inference.get_animal and returns GetAnimalResponse."""

    def GetAnimal(self, request, context):
        start = time.perf_counter()
        text = (request.text or "").strip()
        animal, confidence = inference.get_animal(text)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "request method=GetAnimal status=ok duration_ms=%.2f text_len=%d",
            duration_ms,
            len(text),
        )
        return word2animal_pb2.GetAnimalResponse(animal=animal, confidence=confidence)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logger.debug("%s - %s", self.address_string(), format % args)


def serve_health():
    server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
    logger.info("Health server listening on :%d", HEALTH_PORT)
    server.serve_forever()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    word2animal_pb2_grpc.add_Word2AnimalServicer_to_server(
        Word2AnimalServicer(), server
    )
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    server.start()
    logger.info("Word2Animal gRPC server listening on :%d", GRPC_PORT)
    server.wait_for_termination()


if __name__ == "__main__":
    health_thread = threading.Thread(target=serve_health, daemon=True)
    health_thread.start()
    serve()
