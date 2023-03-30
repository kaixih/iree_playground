import tensorflow as tf

from iree.compiler import tf as tfc

class FuseActivation(tf.Module):

  @tf.function(input_signature=[tf.TensorSpec([16, 8], tf.float32)])
  def my_act(self, input):
    return tf.keras.activations.gelu(input, approximate=True)

compiler_module = tfc.compile_module(
    FuseActivation(), import_only=True,
    import_extra_args=["--output-format=mlir-ir"])

mlir = compiler_module.decode('utf-8')
print(mlir.replace('\\22', ''))
