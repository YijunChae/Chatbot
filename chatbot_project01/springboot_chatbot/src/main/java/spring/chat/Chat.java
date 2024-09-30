package spring.chat;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.SequenceGenerator;

//하이버네티어가 조회할 테이블명
@Entity(name="chat_table")
//일련번호를 생성하는 시퀀스 정보 설정
@SequenceGenerator(
		//설정 이름
		name = "chat_generator",
		//시퀀스 객체 이름
		sequenceName = "chat_seq",
		//1씩 자동으로 증가하는 일련 번호 생성
		allocationSize = 1
		)

public class Chat {
	
	//Primary Key 속성인 채팅 메시지 번호를 저장할 속성
	@Id
	
	//사용할 시퀀스 설정 정보
	@GeneratedValue(
			//시퀀스를 사용하여 일련번호를 생성할 것임
			strategy = GenerationType.SEQUENCE,
			//사용할 시퀀스 설정 이름
			generator = "chat_generator"
			)
	private Long num; //채팅 번호
	
	private String input; //입력한 채팅 메시지
	private String chatbot; //챗봇메시지
	
	public Long getNum() {
		return num;
	}
	public void setNum(Long num) {
		this.num = num;
	}
	public String getInput() {
		return input;
	}
	public void setInput(String input) {
		this.input = input;
	}
	public String getChatbot() {
		return chatbot;
	}
	public void setChatbot(String chatbot) {
		this.chatbot = chatbot;
	}
	
	@Override
	public String toString() {
		return "Chat [num=" + num + ", input=" + input + ", chatbot=" + chatbot + "]";
	}
	
}
