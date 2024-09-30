package spring.chat;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository //데이터베이스와 연동 쿼리를 실행할 인터페이스
//하이버네이트는 이 인터페이스 상속받아서
//데이터베이스와 연동하는 쿼리를 실행하는 클래스를 구현할 것임
public interface JpaChatRepository extends JpaRepository<Chat, Long> {
	//findAll : 전체 채팅 정보 조회
	//OrderByNumDesc : num 컬럼의 내림차순 정렬
	public List<Chat> findAllByOrderByNumDesc();
}
