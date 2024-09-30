package spring.chat;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;

import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.entity.UrlEncodedFormEntity;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.CloseableHttpResponse;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.io.entity.EntityUtils;
import org.apache.hc.core5.http.message.BasicNameValuePair;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.ModelAndView;

@Controller
public class ChatController {

	@Autowired
	JpaChatRepository jpaChat;
	
	// 웹 브라우저에서 http://localhost:8080/ 입력햇을 때 실행
	@RequestMapping(value="/")
	public ModelAndView allChart1() {
		
		// num 컬럼의 내림차순으로 정렬해서 전체 레코드 조회
		List<Chat> allList = jpaChat.findAllByOrderByNumDesc();
		
		ModelAndView mav = new ModelAndView();
		
		// 조회한 모든 채팅 정보를 HTML 페이지로 전송
		mav.addObject("allChat", allList);
		
		// selectChatAll.html 페이지로 이동
		mav.setViewName("selectChatAll");
		
		return mav;
	}
	
	
	// 웹 브라우저에서 http://localhost:8080/insertChatControl 입력했을 때 실행
	@RequestMapping(value="/insertChatControl")
	public ModelAndView insertChatControl(Chat chat) throws Exception {
		
		// 접속할 Rest 서버의 url 설정
		HttpPost httpPost = new HttpPost("http://localhost:5000/chatbot");
		// Rest Server로 전송할 값 설정
		List<BasicNameValuePair> nvps = new ArrayList<>();
		// Rest 서버로 전송할 값을 key value로 설정
		// chat.getInput() : 입력한 채팅 메시지
		nvps.add(new BasicNameValuePair("input_message", chat.getInput()));
		// Rest 서버로 전송할 key value의 한글 인코딩 설정
		httpPost.setEntity(
				new UrlEncodedFormEntity(nvps, Charset.forName("UTF-8")));
		// Rest 서버의 함수를 호출할 객체 생성
		CloseableHttpClient httpclient = HttpClients.createDefault();
		// Rest 서버의 함수를 호출하고 리턴값을 가져올 객체 생성
		CloseableHttpResponse response2 = httpclient.execute(httpPost);
		
		// response2.getEntity() : Rest Server의 리턴값을 가져옴
		// Charset.forName("UTF-8") : Rest Server의 리턴값을 UTF-8로 인코딩
		// EntityUtils.toString(); : Rest Server의 리턴값을 String 으로 변환해서 chat_message 변수에 저장
		String chat_message = 
				EntityUtils.toString(response2.getEntity(),
						Charset.forName("UTF-8"));
		
		System.out.println("챗봇 리턴값 : " + chat_message);
		
		// 채팅 메시지 저장
		chat.setChatbot(chat_message);
		// myChat의 속성을 데이터베이스 저장
		jpaChat.save(chat);
		
		ModelAndView mav = new ModelAndView();
		// 메인페이지로 이동
		mav.setViewName("forward:/");
		return mav;
		
	}
	
}