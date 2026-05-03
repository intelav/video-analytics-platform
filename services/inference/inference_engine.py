from yolo_utils import preprocess,get_cache,set_cache
import numpy as np 
import tritonclient.http as httpclient
import tritonclient.grpc as grpcclient
import pickle

class InferenceEngine:
    def __init__(self, triton_client, redis_client):
        self.client = triton_client
        self.redis = redis_client

    def infer(self, frame):
        inp = preprocess(frame)
        inp = np.expand_dims(inp, axis=0)

        key, cached = get_cache(inp)

        if cached:
            preds = pickle.loads(cached)
        else:
            inputs = [grpcclient.InferInput("images", inp.shape, "FP32")]
            inputs[0].set_data_from_numpy(inp)

            outputs = [grpcclient.InferRequestedOutput("output0")]

            result = self.client.infer("yolov8", inputs, outputs=outputs)
            preds = result.as_numpy("output0")

            set_cache(key, pickle.dumps(preds))

        return preds