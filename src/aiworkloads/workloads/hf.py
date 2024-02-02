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
from datasets import load_dataset, concatenate_datasets


def setup_distributed_training():
    # Initialize distributed environment with environment variables set by SLURM
    rank = int(os.environ["SLURM_PROCID"])
    world_size = int(os.environ["WORLD_SIZE"])
    gpus_per_node = int(os.environ.get("GPUS_PER_NODE", torch.cuda.device_count()))
    local_rank = rank % gpus_per_node

    torch.cuda.set_device(local_rank)
    dist.init_process_group(backend="nccl", rank=rank, world_size=world_size)
    return local_rank


def train_model(
    model_name,
    task,
    dataset_name,
    dataset_config_name,
    batch_size,
    num_epochs,
    learning_rate,
    model_save_path,
):
    local_rank = setup_distributed_training()

    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name).to(
        local_rank
    )

    # Make the model DistributedDataParallel
    model = DDP(model, device_ids=[local_rank], output_device=local_rank)

    # Load and preprocess the dataset
    raw_datasets = load_dataset(dataset_name, dataset_config_name)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    tokenized_datasets = raw_datasets.map(tokenize_function, batched=True)
    tokenized_datasets = tokenized_datasets.remove_columns(["text"])
    tokenized_datasets.set_format("torch")

    # Create a distributed sampler
    train_sampler = torch.utils.data.distributed.DistributedSampler(
        tokenized_datasets["train"], num_replicas=world_size, rank=rank
    )

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=model_save_path,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        do_train=True,
        do_eval=True,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        logging_dir="./logs",
        report_to="none",  # Disable logging to WANDB or other external services.
        local_rank=local_rank,  # Important for Hugging Face to recognize distributed training
    )

    # Initialize Trainer
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

    # Train the model
    trainer.train()

    # Save the model, but only on the main process
    if local_rank == 0:
        model.module.save_pretrained(model_save_path)


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
    args = parser.parse_args()

    train_model(
        args.model_name,
        args.task,
        args.dataset_name,
        args.dataset_config_name,
        args.batch_size,
        args.num_epochs,
        args.learning_rate,
        args.model_save_path,
    )


if __name__ == "__main__":
    main()
