import tensorflow as tf
import keras_hub

from src.utils.config import MAX_SEQ_LENGTH, LABEL_COLUMNS

# keras_hub preset name — alag hai HF slug se, isliye config.py mein nahi daala
KERAS_HUB_PRESET = "distil_bert_base_en_uncased"


def build_model(dropout_rate=0.3):
    input_ids = tf.keras.Input(
        shape=(MAX_SEQ_LENGTH,), dtype=tf.int32, name="input_ids"
    )
    attention_mask = tf.keras.Input(
        shape=(MAX_SEQ_LENGTH,), dtype=tf.int32, name="attention_mask"
    )

    backbone = keras_hub.models.DistilBertBackbone.from_preset(KERAS_HUB_PRESET)
    sequence_output = backbone({"token_ids": input_ids, "padding_mask": attention_mask})
    cls_token = sequence_output[:, 0, :]

    x = tf.keras.layers.Dropout(dropout_rate)(cls_token)
    x = tf.keras.layers.Dense(128, activation="relu")(x)
    x = tf.keras.layers.Dropout(dropout_rate)(x)
    outputs = tf.keras.layers.Dense(
        len(LABEL_COLUMNS), activation="sigmoid", name="labels"
    )(x)

    model = tf.keras.Model(
        inputs={"input_ids": input_ids, "attention_mask": attention_mask},
        outputs=outputs,
    )
    return model
