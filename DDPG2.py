import numpy as np
import random
import tensorflow as tf
from keras import Model
from keras import layers
from keras import optimizers
from keras import initializers
from keras import ops
from collections import deque
from qunoise import QUNoise

REPLAY_MEMORY_SIZE=50_000
MIN_REPLAY_MEMORY_SIZE = 500
MINIBATCH_SIZE=64

GAMMA =0.99
CRITIC_LR=0.002
ACTOR_LR=0.001
TAU=0.005

class DDPGAgent:
    def __init__(self,input_shape,num_states,num_actions):
        self.actor_model=self.CreateActor(input_shape,num_actions)
        self.critic_model=self.CreateCritic(num_states,num_actions)

        self.target_actor=self.CreateActor(input_shape,num_actions)
        self.target_critic=self.CreateCritic(num_states,num_actions)

        self.target_actor.set_weights(self.actor_model.get_weights())
        self.target_critic.set_weights(self.critic_model.get_weights())

        self.critic_optimizer=optimizers.Adam(CRITIC_LR)
        self.actor_optimizer=optimizers.Adam(ACTOR_LR)

        self.replay_memory = deque(maxlen=REPLAY_MEMORY_SIZE)

        self.noise=QUNoise(mu=np.zeros(6),sigma=float(0.2)*np.ones(6))

    @staticmethod
    def CreateActor(input_shape,num_actions):
        last_init=initializers.RandomUniform(minval=-0.003,maxval=0.003)
        inputs=layers.Input(shape=input_shape)
        out = layers.Dense(256,activation="relu")(inputs)
        out = layers.Dense(256,activation="relu")(out)

        outputs1 = layers.Dense(num_actions//2, activation="sigmoid", kernel_initializer=last_init)(out)
        outputs1 = layers.Lambda(lambda x:x*800)(outputs1)
        
        outputs2 = layers.Dense(num_actions//2, activation="tanh", kernel_initializer=last_init)(out)
        outputs2 = layers.Lambda(lambda x:x*45)(outputs2)

        outputs=layers.Concatenate()([outputs1,outputs2])
        model= Model(inputs,outputs)
        return model
    
    @staticmethod
    def CreateCritic(num_states,num_actions):
        state_input=layers.Input(shape=(num_states,))
        state_out = layers.Dense(16,activation="relu")(state_input)
        state_out = layers.Dense(32, activation="relu")(state_out)

        action_input=layers.Input(shape=(num_actions,))
        action_out= layers.Dense(32, activation="relu")(action_input)

        concat = layers.Concatenate()([state_out, action_out])

        out=layers.Dense(256,activation="relu")(concat)
        out=layers.Dense(256,activation="relu")(out)
        outputs =layers.Dense(1)(out)

        model=Model([state_input,action_input],outputs)

        return model
    
    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    def train(self):
        if len(self.replay_memory) < MINIBATCH_SIZE:
            return

        minibatch=random.sample(self.replay_memory, MINIBATCH_SIZE)

        current_states=tf.convert_to_tensor([transition[0] for transition in minibatch])
        
        actions=tf.convert_to_tensor([transition[1] for transition in minibatch])
        rewards=tf.convert_to_tensor([transition[2] for transition in minibatch])
        rewards=tf.cast(rewards,dtype="float32")
        next_states=tf.convert_to_tensor([transition[3] for transition in minibatch])
        
        with tf.GradientTape() as tape:
           target_actions=self.target_actor(next_states,training=True)
           y=rewards +GAMMA * self.target_critic([next_states,target_actions],training=True)
           critic_value=self.critic_model([current_states,actions],training=True)
           critic_loss=ops.mean(ops.square(y-critic_value))
        critic_grad=tape.gradient(critic_loss,self.critic_model.trainable_variables)
        self.critic_optimizer.apply_gradients(zip(critic_grad,self.critic_model.trainable_variables))

        with tf.GradientTape() as tape:
            actions=self.actor_model(current_states,training=True)
            critic_value=self.critic_model([current_states,actions],training=True)
            actor_loss=-ops.mean(critic_value)
        actor_grad = tape.gradient(actor_loss,self.actor_model.trainable_variables)
        self.actor_optimizer.apply_gradients(zip(actor_grad,self.actor_model.trainable_variables))
    
    @staticmethod
    def UpdateTarget(target,orginal):
        target_weights=target.get_weights()
        orginal_weights=orginal.get_weights()

        for i in range(len(target_weights)):
            target_weights[i]=orginal_weights[i] * TAU +target_weights[i] *(1-TAU)
        target.set_weights(target_weights)
    

    def policy(self,current_state):
        current_state=ops.expand_dims(
            tf.convert_to_tensor(current_state),axis=0
        )
        actions=ops.squeeze(self.actor_model(current_state))
        actions=actions.numpy()
        actions+=self.noise()
        actions[:3]=np.clip(actions[:3],0,800)
        actions[3:]=np.clip(actions[3:],-45,45)
        return actions


