package spring.chat;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
public class ChatSelectTest01 {
	@Autowired //JpaChatRepository 인터페이스 상속받아서
	//SQL 쿼리를 실행하는 메서드가 구현된 클래스 객체를 자동으로 대입받을 변수
	//해당 객체는 Up-Casting으로 부모타입 인터페이스 변수에 저장
	JpaChatRepository chatRepository;
	
	@Test
	public void chatJpaTest() {
		//num 컬럼의 내림차순으로 정렬해서 조회
		List<Chat> chatList =  chatRepository.findAllByOrderByNumDesc();
		System.out.println("chatList="+chatList);
	}

}
