package spring.chat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
public class ChatInsertTest01 {
	@Autowired //JpaChatRepository 인터페이스를 상속받아서
	//SQL 쿼리를 실행하는 메서드가 구현된 클래스 객체를 자동으로 대입받을 변수
	//해당 객체는 Up-Casting으로 부모타입 인터페이스 변수에 저장
	JpaChatRepository chatRepository;
	
	@Test
	public void chatJpaTest() {
		//데이터베이스에 저장할 정보를 속성으로 갖는 객체 생성
		Chat c1 = new Chat();
		c1.setInput("주말 잘 지내");
		c1.setChatbot("즐거운 주말 되세요");
		
		//데이터베이스에 속성값 저장
		chatRepository.save(c1);
		
		//데이터베이스에 저장할 정보를 속성으로 갖는 객체 생성
		Chat c2 = new Chat();
		c2.setInput("오늘은 불금");
		c2.setChatbot("즐거운 금요일 되세요");
		
		//데이터베이스에 속성값 저장
		chatRepository.save(c2);
	}
}
