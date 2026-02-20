OUTPUT_PATH="data/used_cars_vehicles/"

python train_ditto.py \
  --task used_cars_vehicles \
  --batch_size 32 \
  --run_id 1 \
  --logdir ${OUTPUT_PATH}log \
  --save_model \
  --lm roberta \
  --finetuning \
  --lr 1.5e-5 \
  --n_epochs 5 \
  --device cuda \
