import argparse
import os
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset


def setup_distributed_training(scheduler_type):
    """
    Setup distributed training environment based on the job scheduler type.
    """
    if scheduler_type == "slurm":
        rank = int(os.environ.get("SLURM_PROCID", 0))
        world_size = int(os.environ.get("WORLD_SIZE", 1))
        gpus_per_node = int(os.environ.get("GPUS_PER_NODE", torch.cuda.device_count()))
    elif scheduler_type == "k8":
        rank = int(os.environ.get("K8_NODE_RANK", 0))
        world_size = int(os.environ.get("K8_NUM_NODES", 1))
        gpus_per_node = int(
            os.environ.get("GPUS_PER_NODE", torch.cuda.device_count())
        )  # Assuming this is set in Kubernetes as well
    else:
        rank = 0
        world_size = 1
        gpus_per_node = torch.cuda.device_count()

    local_rank = rank % gpus_per_node
    torch.cuda.set_device(local_rank)
    dist.init_process_group(backend="nccl", rank=rank, world_size=world_size)
    return local_rank


def train_model(args):
    local_rank = setup_distributed_training(args.scheduler_type)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(args.model_name).to(
        local_rank
    )

    model = DDP(model, device_ids=[local_rank], output_device=local_rank)

    raw_datasets = load_dataset(args.dataset_name, args.dataset_config_name)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    tokenized_datasets = raw_datasets.map(tokenize_function, batched=True)
    tokenized_datasets = tokenized_datasets.remove_columns(["text"])
    tokenized_datasets.set_format("torch")

    training_args = TrainingArguments(
        output_dir=args.model_save_path,
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        do_train=True,
        do_eval=True,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        logging_dir=args.results_save_path,
        report_to="none",
        local_rank=local_rank,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=lambda data: {
            "input_ids": torch.stack([f["input_ids"] for f in data]),
            "attention_mask": torch.stack([f["attention_mask"] for f in data]),
            "labels": torch.tensor([f["labels"] for f in data]),
        },
        tokenizer=tokenizer,
    )

    trainer.train()

    if local_rank == 0:
        model.module.save_pretrained(args.model_save_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--task", type=str, required=True)
    parser.add_argument("--dataset_name", type=str, required=True)
    parser.add_argument("--dataset_config_name", type=str, default=None)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--num_epochs", type=int, default=3)
    parser.add_argument("--learning_rate", type=float, default=5e-5)
    parser.add_argument("--model_save_path", type=str, required=True)
    parser.add_argument("--results_save_path", type=str, required=True)
    parser.add_argument(
        "--scheduler_type", type=str, required=True
    )  # New argument to pass scheduler type
    args = parser.parse_args()

    train_model(args)


if __name__ == "__main__":
    main()
