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


def setup_distributed_training():
    # Set up the distributed training environment
    torch.distributed.init_process_group(backend="nccl")


def train_model(
    model_name,
    task,
    dataset_name,
    dataset_config,
    batch_size,
    num_epochs,
    learning_rate,
    model_save_path,
):
    setup_distributed_training()

    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Make the model DistributedDataParallel
    model = DDP(model)

    # Load and preprocess the dataset
    dataset = load_dataset(dataset_name, dataset_config)
    tokenized_dataset = dataset.map(
        lambda x: tokenizer(x["text"], padding=True, truncation=True), batched=True
    )

    # Use DistributedSampler for distributed training
    train_sampler = torch.utils.data.DistributedSampler(tokenized_dataset["train"])
    eval_sampler = torch.utils.data.DistributedSampler(tokenized_dataset["validation"])

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=model_save_path,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        do_train=True,
        do_eval=True,
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
        train_sampler=train_sampler,
        eval_sampler=eval_sampler,
    )

    # Train the model
    trainer.train()

    # Save the model
    model.module.save_pretrained(model_save_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--task", type=str, required=True)
    parser.add_argument("--dataset", type=str, required=True)
    parser.add_argument("--dataset_config", type=str, default=None)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--num_epochs", type=int, default=3)
    parser.add_argument("--learning_rate", type=float, default=5e-5)
    parser.add_argument("--model_save_path", type=str, required=True)
    args = parser.parse_args()

    train_model(
        args.model_name,
        args.task,
        args.dataset,
        args.dataset_config,
        args.batch_size,
        args.num_epochs,
        args.learning_rate,
        args.model_save_path,
    )


if __name__ == "__main__":
    # Detect if we are in a multi-node environment and set up accordingly
    if "WORLD_SIZE" in os.environ:
        main()
    else:
        print("This script is intended to be run in a distributed environment.")
