import argparse
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset


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
    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Load and preprocess the dataset
    dataset = load_dataset(dataset_name, dataset_config)
    tokenized_dataset = dataset.map(
        lambda x: tokenizer(x["text"], padding=True, truncation=True), batched=True
    )

    # Define training arguments
    training_args = TrainingArguments(
        output_dir=model_save_path,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
    )

    # Train the model
    trainer.train()

    # Save the model
    model.save_pretrained(model_save_path)


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
    main()
