from flask import Flask
from flask import request

from tensorflow.keras import models
import numpy as np
import pickle
from konlpy.tag import Twitter
import re
import os
import sys

app = Flask(__name__)

# 태그 단어
PAD = "<PADDING>"   # 패딩(입력 데이터의 개수)
                    # 한 문장에 단어의 개수가 30개 미만일 경우
                    # <PADDING>으로 채워넣음

STA = "<START>"     # 디코더가 Answer 시작하는 기호

END = "<END>"       # 디코더가 Answer를 끝내는 기호

OOV = "<OOV>"       # 학습한 단어가 아닌 단어가
                    # 입력으로 들어 왔을 때
                    # (Out Of Vocabulary) 로 변환

# 태그 인덱스
# 30글자 미만의 입력이 입력됐을 때
# 0으로 변환
PAD_INDEX = 0

# 디코더가 Answer를 시작하는 숫자 1
STA_INDEX = 1

# 디코더가 Answer를 끝내는 숫자 2
END_INDEX = 2

# 입력 시 학습하지 않은 단어가 입력됐을 때
# 3으로 변환
OOV_INDEX = 3

# 데이터 타입
ENCODER_INPUT = 0   # Question 입력을 처리하는 인코더의 입력
DECODER_INPUT = 1   # Answer 입력을 처리하는 디코더의 입력
DECODER_OUTPUT = 2  # 실제 Answer 의 값

# 한 문장에서 단어 시퀀스의 최대 개수
# 한 문장당 30개씩 단어를 입력받음
max_sequences = 30

# 파이썬 모델이 저장된 경로
path= "."
# 모델 파일 로드
encoder_model = models.load_model(path + '/seq2seq_chatbot_encoder_model.h5')
decoder_model = models.load_model(path + '/seq2seq_chatbot_decoder_model.h5')

# 인덱스 파일 로드
with open(path + '/word_to_index.pkl', 'rb') as f:
    word_to_index = pickle.load(f)
with open(path + '/index_to_word.pkl', 'rb') as f:
    index_to_word = pickle.load(f)


# 형태소분석 함수

def pos_tag(sentences):
    # KoNLPy 형태소분석기 설정
    tagger = Twitter()

    # 문장을 단어 단위로 잘라서 저장할 리스트
    sentences_pos = []

    # 모든 문장 반복
    for sentence in sentences:
        # [.,!?\"':;~()] : 특수 기호를 찾을 객체
        RE_FILTER = re.compile("[.,!?\"':;~()]")
        # re.sub(RE_FILTER, "", sentence) :
        # sentence에서
        # RE_FILTER 에 설정된 특수기호를 "" 로 변환(삭제)
        # 해서 리턴
        sentence = re.sub(RE_FILTER, "", sentence)

        # tagger.morphs(sentence) : sentence를 단어 단위로 분리하여 리스트에 넣음
        # " ".join(tagger.morphs(sentence)) :
        # 단어와 단어 사이에 " " 추가해서 문자열 리턴
        sentence = " ".join(tagger.morphs(sentence))

        # 단어 단위로 분리된 sentence를 sentences_pos 에 추가
        sentences_pos.append(sentence)

    return sentences_pos


# 문장의 단어를 숫자로 변환

def convert_text_to_index(sentences, vocabulary, type):
    # 모든 줄의 단어를 숫자로 변환한 데이터를 저장할 리스트
    sentences_index = []

    # sentences 에서 1줄 sentence 에 대입
    for sentence in sentences:
        # 1줄의 단어를 숫자로 변환해서 저장할 리스트
        sentence_index = []

        # 디코더 입력일 경우 맨 앞에 START 태그 추가
        if type == DECODER_INPUT:
            sentence_index.extend([vocabulary[STA]])

        # for word in sentence.split() : 단어 1개씩 리턴해서 변수 word에 저장
        for word in sentence.split():
            # 사전에 있는 단어면
            if vocabulary.get(word) is not None:
                # 해당 인덱스를 추가
                sentence_index.extend([vocabulary[word]])
            else:
                # 사전에 없는 단어면 OOV 인덱스를 추가
                sentence_index.extend([vocabulary[OOV]])

        # DECODER_TARGET : label 데이터일 경우 최대 길이 검사
        if type == DECODER_OUTPUT:
            # len(sentence_index) : 문장을 숫자로 변환한 데이터의 길이
            # max_sequences : 최대 입력 길이 (30)
            if len(sentence_index) >= max_sequences:
                # sentence_index[:max_sequences-1] : 인덱스 0~29미만까지 자르고
                # [vocabulary[END]] : 마지막에 END 추가
                sentence_index = sentence_index[:max_sequences - 1] + [vocabulary[END]]
            else:
                # sentence_index 마지막에 END 추가
                sentence_index += [vocabulary[END]]
        else:   # label 데이터가 아닌 입력 데이터의 경우
            if len(sentence_index) > max_sequences:
                # 0~30미만의 데이터까지 자름
                sentence_index = sentence_index[:max_sequences]

        # 최대 길이에 없는 공간은 패딩 인덱스로 채움
        sentence_index += (max_sequences - len(sentence_index)) * [vocabulary[PAD]]

        # 문장의 인덱스 배열을 추가
        sentences_index.append(sentence_index)

    return np.asarray(sentences_index)


# 인덱스를 문장으로 변환
def convert_index_to_text(indexs, vocabulary):
    sentence = ''

    # 모든 문장에 대해서 반복
    for index in indexs:
        if index == END_INDEX:
            # 종료 인덱스면 중지
            break
        elif vocabulary.get(index) is not None:
            # 사전에 있는 인덱스면 해당 단어를 추가
            sentence += vocabulary[index]
        else:
            # 사전에 없는 인덱스면 OOV 단어를 추가
            sentence += vocabulary[OOV_INDEX]

        # 빈칸 추가
        sentence += ' '

    return sentence


# 예측을 위한 입력 생성

def make_predict_input(sentence):
    sentences = []
    # 입력을 추가
    sentences.append(sentence)
    # 특수문자를 삭제하고 단어와 단어 사이에 공백 추가해서 리턴
    sentences = pos_tag(sentences)
    # 단어를 숫자로 변환
    input_seq = convert_text_to_index(sentences, word_to_index, ENCODER_INPUT)

    return input_seq


# 챗봇이 단어를 1개씩 예측해서 리턴하는 함수
def generate_text(input_seq):
    # 입력을 인코더에 넣어 마지막 상태 리턴
    states = encoder_model.predict(input_seq)

    # 디코더 입력 초기화 0으로
    target_seq = np.zeros((1, 1))

    # 디코더 입력 첫 번째에 <START> 태그 추가
    target_seq[0, 0] = STA_INDEX

    # 인덱스, 초기화
    indexs = []

    # 디코더 타임 스텝 반복
    while 1:
        # 디코더로 현재 타임 스텝 출력 구함
        # 처음에는 인코더 상태를, 다음부터 이전 디코더 상태로 예측하고
        # 챗봇 메시지는 decoder_outputs에 저장
        decoder_outputs, state_h, state_c = decoder_model.predict(
            [target_seq] + states)

        # 결과의 원핫인코딩 형식을 인덱스로 변환
        index = np.argmax(decoder_outputs[0, 0, :])
        # 챗봇이 예측한 단어를 indexs에 추가
        indexs.append(index)

        # 30글자 이상이면 종료
        if index == END_INDEX or len(indexs) >= max_sequences:
            break

        # 디코더 입력 0으로 초기화
        target_seq = np.zeros((1, 1))
        # 챗봇 모델이 예측한 데이터를 다음 입력으로 설정
        target_seq[0, 0] = index

        # 디코더의 이전 상태를 디코더 다음 예측에 사용
        states = [state_h, state_c]

    # 인덱스를 문장으로 변환
    sentence = convert_index_to_text(indexs, index_to_word)
    # 챗봇이 예측한 문장 리턴
    return sentence

# post 방식의 chatbot url을 입력하면 함수가 호출되는 rest server의 메서드
@app.route('/chatbot', methods=['POST'])
def chatbot_rest_server():
    # 입력 메시지 리턴
    input_message = request.form.get('input_message', "입력값 없음")
    print('input_message', input_message)

    # 문장을 인덱스로 변환
    input_seq = make_predict_input(input_message)

    # 예측 모델로 텍스트 생성
    sentence = generate_text(input_seq)
    # 예측 모델로 생성한 텍스트 리턴
    return sentence




@app.route('/hello_rest_server', methods=['POST'])
def hello_world():    # put application's code here
    return '안녕 난 rest server야'


# post 방식의 param_rest_server url을 입력하면 함수가 호출되는 rest server의 메서드
@app.route("/param_rest_server", methods=['POST'])
def hello_rest2():
    # Rest Server로 전송한 name 파라미터의 값을 꺼내서 param_name 변수에 저장
    param_name = request.form.get('name', '입력값 없음') # 후자는 입력 파라미터가 없을 때 리턴하는 부분
    print("param_name = ", param_name)
    # 리턴값
    return "그래 너의 이름은 " + param_name + "이구나!!"

if __name__ == '__main__':
    app.run()