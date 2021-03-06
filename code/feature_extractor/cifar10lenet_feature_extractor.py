## Copyright 2019 Gia-Lac TRAN,  Edwin V. Bonilla, John P. Cunningham, Pietro Michiardi, and Maurizio Filippone
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

import tensorflow as tf
import feature_extractor.feature_extractor as feature_extractor

class Cifar10lenet_Feature_Extractor(feature_extractor.Feature_Extractor):
	def __init__(self, in_channel=3, keep_prob=0.5):
		self.keep_prob = keep_prob
		self.d_feature = 8 * 8 * 64
		
		# Define lenet structure
		self.w1 = tf.Variable(tf.truncated_normal([5,5,3,64], stddev=0.1), tf.float32)
		self.b1 = tf.Variable(tf.truncated_normal([64], stddev=0.1), tf.float32)
		self.w2 = tf.Variable(tf.truncated_normal([5,5,64,64], stddev=0.1), tf.float32)
		self.b2 = tf.Variable(tf.truncated_normal([64], stddev=0.1), tf.float32)
		
		self.conv_filters = [self.w1, self.w2]
	
	# OVERWRITEN METHOD
	def feed_forward(self, x):
		h1 = tf.nn.conv2d(x, self.w1, strides=[1,1,1,1], padding = "SAME")
		h1_relu = tf.nn.relu(h1 + self.b1) # [batch_size, 32, 32, 64]
		h1_pooled = tf.nn.max_pool(h1_relu, ksize=[1,3,3,1], strides=[1,2,2,1], padding="SAME") # [batch_size, 32, 32, 64]
		h1_pooled_norm = tf.nn.lrn(h1_pooled, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75) #[batch_size, 32, 32, 64]
		
		h1_mcd = tf.nn.dropout(h1_pooled_norm, keep_prob=self.keep_prob) * self.keep_prob
		h2 = tf.nn.conv2d(h1_mcd, self.w2, strides=[1,1,1,1], padding="SAME")
		h2_relu = tf.nn.relu(h2 + self.b2) # [batch_size, 16, 16, 64]
		h2_relu_norm = tf.nn.lrn(h2_relu, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75)
		h2_pooled = tf.nn.max_pool(h2_relu_norm, ksize=[1,3,3,1], strides=[1,2,2,1], padding="SAME") # [batch_size, 8, 8, 64]
		
		h2_pooled_flat = tf.reshape(h2_pooled, [-1, 8 * 8 * 64])
		
		return h2_pooled_flat
	
	# OVERWRITEN METHOD
	def get_cnn_name(self):
		return "cifar10lenet"
	
	# OVERWRITEN METHOD
	def get_d_feature(self):
		return self.d_feature
	
	# OVERWRITEN METHOD
	def get_conv_params(self):
		return self.conv_filters
	
	# OVERWRITEN METHOD
	def get_regu_loss(self):
		regu_loss = tf.nn.l2_loss(self.w1) + self.keep_prob * tf.nn.l2_loss(self.w2)
		regu_loss = regu_loss + tf.nn.l2_loss(self.b1) + tf.nn.l2_loss(self.b2)
		return regu_loss