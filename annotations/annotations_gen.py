import time
import random


def mock_annotation_processing():
    # Simulate a CPU-intensive process by sleeping for some time
    time.sleep(10)  # You can adjust the sleep time based on your simulation needs

    # Generate random annotations
    annotations = [
        "mountain",
        "sea",
        "table",
        "chair",
        "forest",
        "building",
        "car",
        "flower",
    ]
    return random.choice(annotations)
