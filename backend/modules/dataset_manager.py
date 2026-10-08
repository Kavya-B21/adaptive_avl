import json
import random
from pathlib import Path
from datetime import datetime


class DatasetManager:

    SUPPORTED_WORKLOADS = {
        "random",
        "ascending",
        "descending",
        "alternating"
    }

    def __init__(
        self,
        dataset_directory="datasets"
    ):

        self.dataset_directory = Path(
            dataset_directory
        )

        self.dataset_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    def validate_size(self, size):

        if not isinstance(size, int):
            raise TypeError(
                "Dataset size must be an integer."
            )

        if size <= 0:
            raise ValueError(
                "Dataset size must be greater than zero."
            )

        return True

    def generate_random(
        self,
        size,
        seed=None
    ):

        self.validate_size(size)

        rng = random.Random(seed)

        return rng.sample(
            range(size * 10),
            size
        )

    def generate_ascending(self, size):

        self.validate_size(size)

        return list(range(size))

    def generate_descending(self, size):

        self.validate_size(size)

        return list(
            range(size - 1, -1, -1)
        )

    def generate_alternating(self, size):

        self.validate_size(size)

        result = []

        low = 0
        high = size - 1

        while low <= high:

            result.append(low)

            low += 1

            if low <= high:

                result.append(high)

                high -= 1

        return result

    def generate(
        self,
        workload_type,
        size,
        seed=None
    ):

        workload_type = (
            workload_type
            .lower()
            .strip()
        )

        if workload_type not in (
            self.SUPPORTED_WORKLOADS
        ):

            raise ValueError(
                f"Unsupported workload type: "
                f"{workload_type}"
            )

        if workload_type == "random":
            return self.generate_random(
                size,
                seed
            )

        if workload_type == "ascending":
            return self.generate_ascending(
                size
            )

        if workload_type == "descending":
            return self.generate_descending(
                size
            )

        if workload_type == "alternating":
            return self.generate_alternating(
                size
            )

    def validate_dataset(
        self,
        dataset,
        expected_size=None
    ):

        if not isinstance(dataset, list):
            raise TypeError(
                "Dataset must be a list."
            )

        if len(dataset) == 0:
            raise ValueError(
                "Dataset cannot be empty."
            )

        if expected_size is not None:

            if len(dataset) != expected_size:
                raise ValueError(
                    "Dataset size mismatch."
                )

        if not all(
            isinstance(value, int)
            for value in dataset
        ):

            raise TypeError(
                "Dataset values must be integers."
            )

        if len(dataset) != len(set(dataset)):

            raise ValueError(
                "Dataset contains duplicate keys."
            )

        return True

    def get_statistics(self, dataset):

        self.validate_dataset(dataset)

        return {
            "size": len(dataset),
            "minimum": min(dataset),
            "maximum": max(dataset),
            "unique_values": len(set(dataset)),
            "is_sorted_ascending":
                dataset == sorted(dataset),
            "is_sorted_descending":
                dataset == sorted(
                    dataset,
                    reverse=True
                )
        }

    def generate_experiment_id(
        self,
        workload_type,
        size,
        seed=None
    ):

        seed_value = (
            "none"
            if seed is None
            else str(seed)
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        return (
            f"{workload_type}_"
            f"{size}_"
            f"{seed_value}_"
            f"{timestamp}"
        )

    def save_experiment(
        self,
        dataset,
        workload_type,
        seed=None
    ):

        self.validate_dataset(dataset)

        experiment_id = (
            self.generate_experiment_id(
                workload_type,
                len(dataset),
                seed
            )
        )

        experiment = {

            "experiment_id":
                experiment_id,

            "metadata": {

                "workload_type":
                    workload_type,

                "size":
                    len(dataset),

                "seed":
                    seed,

                "created_at":
                    datetime.now().isoformat()
            },

            "statistics":
                self.get_statistics(dataset),

            "data":
                dataset
        }

        filename = (
            f"{experiment_id}.json"
        )

        filepath = (
            self.dataset_directory /
            filename
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                experiment,
                file,
                indent=4
            )

        return {
            "experiment_id":
                experiment_id,

            "filename":
                filename,

            "filepath":
                str(filepath)
        }

    def load_experiment(
        self,
        filename
    ):

        filepath = (
            self.dataset_directory /
            filename
        )

        if not filepath.exists():

            raise FileNotFoundError(
                "Experiment file not found."
            )

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            experiment = json.load(file)

        self.validate_dataset(
            experiment["data"]
        )

        return experiment