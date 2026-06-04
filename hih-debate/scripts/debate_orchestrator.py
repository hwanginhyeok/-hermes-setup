#!/usr/bin/env python3
"""
hih-debate 토론 오케스트레이터
다중 AI 모델 간 토론을 자동화하는 Python 스크립트
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

class DebateOrchestrator:
    def __init__(self, session_name=None, topic=""):
        self.session = session_name or os.environ.get("HIH_DEBATE_SESSION", os.path.basename(os.getcwd()))
        self.topic = topic
        self.timestamp = int(datetime.now().timestamp())
        self.debate_dir = f"/tmp/hih_debate_{self.timestamp}"
        self.participants = []
        
    def setup(self):
        """토론 환경 설정"""
        # 디렉토리 생성
        os.makedirs(self.debate_dir, exist_ok=True)
        print(f"📁 토론 디렉토리: {self.debate_dir}")
        
        # 세션 확인
        result = subprocess.run(
            ["tmux", "has-session", "-t", self.session],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ 세션 '{self.session}' 없음")
            return False
        
        # pane 수 확인
        result = subprocess.run(
            ["tmux", "list-panes", "-t", self.session],
            capture_output=True,
            text=True
        )
        pane_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        if pane_count < 2:
            print(f"❌ 최소 2개 pane 필요 (현재: {pane_count})")
            return False
        
        print(f"✅ 세션 '{self.session}' 확인 (pane: {pane_count})")
        
        # 주제 저장
        if self.topic:
            topic_file = os.path.join(self.debate_dir, "topic.md")
            with open(topic_file, 'w') as f:
                f.write(f"# 토론 주제\n\n{self.topic}\n")
            print(f"✅ 주제 저장: {topic_file}")
        
        return True
    
    def start_agent(self, pane_num, agent_type):
        """특정 pane에 에이전트 시작"""
        if agent_type == "claude":
            cmd = f"claude --name debate-claude --add-dir {self.debate_dir}"
            self.participants.append(("Claude", pane_num))
        elif agent_type == "glm":
            cmd = f"claude --model glm-4.6 --name debate-glm --add-dir {self.debate_dir}"
            self.participants.append(("GLM", pane_num))
        elif agent_type == "codex":
            if not self._check_codex():
                print(f"⚠️  Codex 미설치, pane {pane_num} 생략")
                return False
            cmd = f"codex exec --name debate-codex"
            self.participants.append(("Codex", pane_num))
        else:
            print(f"❌ 알 수 없는 에이전트 타입: {agent_type}")
            return False
        
        # tmux로 전송
        subprocess.run([
            "tmux", "send-keys", "-t", f"{self.session}.{pane_num}", cmd, "Enter"
        ])
        time.sleep(2)
        return True
    
    def _check_codex(self):
        """Codex 설치 확인"""
        result = subprocess.run(
            ["which", "codex"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def run_round(self, round_num, agent_pairs):
        """
        특정 라운드 실행
        
        Args:
            round_num: 라운드 번호 (1, 2, 3)
            agent_pairs: [(agent_name, prompt_file), ...]
        """
        print(f"\n🔄 Round {round_num} 시작...")
        
        for agent_name, prompt_file in agent_pairs:
            output_file = os.path.join(self.debate_dir, f"{agent_name.lower()}_round{round_num}.md")
            prompt_content = self._generate_prompt(round_num, agent_name, prompt_file)
            
            # 프롬프트 파일 생성
            prompt_path = os.path.join(self.debate_dir, f"{agent_name.lower()}_round{round_num}_prompt.txt")
            with open(prompt_path, 'w') as f:
                f.write(prompt_content)
            
            # 해당 agent의 pane 찾기
            pane_num = next((p[1] for p in self.participants if p[0] == agent_name), None)
            if pane_num is None:
                print(f"⚠️  {agent_name} pane 없음, 생략")
                continue
            
            # 전송
            subprocess.run([
                "tmux", "send-keys", "-t", f"{self.session}.{pane_num}",
                f"cat {prompt_path}", "Enter"
            ])
            
            print(f"✅ {agent_name} (pane {pane_num})에 Round {round_num} 전송")
        
        # 대기
        wait_time = 60 if round_num == 1 else 90
        print(f"⏳ {wait_time}초 대기...")
        time.sleep(wait_time)
    
    def _generate_prompt(self, round_num, agent_name, reference_file=None):
        """프롬프트 생성"""
        base_prompt = f"""
**Round {round_num} - {agent_name}**

**토론 주제**:
{self.topic}
"""
        
        if round_num == 1:
            if agent_name == "Claude":
                return base_prompt + """
**당신의 페르소나**: 균형 잡힌, 철학적, 윤리적 관점의 분석가

**입장 제시 가이드**:
1. 핵심 주장 (1문장)
2. 근거 3개 이상 (논리적, 경험적, 실증적)
3. 예상 반론에 대한 예방적 방어

500단어 이내로 작성하세요. 시작하세요.
"""
            elif agent_name == "GLM":
                return base_prompt + """
**당신의 페르소나**: 창의적, 다문화적, 비서구적 관점의 혁신가

**입장 제시 가이드**:
1. 핵심 주장 (1문장) - Claude와 차별화
2. 근거 3개 이상 - 아시아적, 다문화적 관점
3. 예상 반론에 대한 예방적 방어

500단어 이내로 작성하세요. 시작하세요.
"""
        
        elif round_num == 2:
            opponent = "GLM" if agent_name == "Claude" else "Claude"
            ref_file = os.path.join(self.debate_dir, f"{opponent.lower()}_round1.md")
            
            return base_prompt + f"""
**{opponent}의 입장을 읽고 비판하세요**:
파일: {ref_file}

**비판 가이드**:
1. {opponent} 입장의 논리적 오류 2개 이상 지적
2. 반례 제시
3. 당신의 입장 강화

400단어 이내로 작성하세요. 시작하세요.
"""
        
        elif round_num == 3:
            opponent = "GLM" if agent_name == "Claude" else "Claude"
            ref_file = os.path.join(self.debate_dir, f"{opponent.lower()}_round2.md")
            
            return base_prompt + f"""
**{opponent}의 비판을 읽고 답변하세요**:
파일: {ref_file}

**답변 가이드**:
1. 비판 수용 또는 반박
2. 입장 수정·보완
3. 타협점 제시 (가능한 경우)

300단어 이내로 작성하세요. 시작하세요.
"""
        
        return ""
    
    def synthesis(self):
        """PM 시너지sis"""
        print("\n🔄 PM 시너지sis 시작...")
        
        synthesis_prompt = f"""
**Final: 시너지sis 단계**

당신은 토론 중재자입니다. 다음 입장들을 읽고 종합하세요:

**Claude의 입장 (최종)**:
파일: {os.path.join(self.debate_dir, "claude_round3.md")}

**GLM의 입장 (최종)**:
파일: {os.path.join(self.debate_dir, "glm_round3.md")}

**시너지sis 가이드**:
1. 공통점 발견 (3개 이상)
2. 핵심 차이점 분석 (왜 다른지)
3. 통합적 결론 도출
4. 추가 연구 필요 사항

800단어 이내로 작성하세요.
"""
        
        synthesis_file = os.path.join(self.debate_dir, "synthesis_prompt.txt")
        with open(synthesis_file, 'w') as f:
            f.write(synthesis_prompt)
        
        print("📄 시너지sis 프롬프트 생성 완료")
        print(synthesis_prompt)
        print(f"\n💾 파일: {synthesis_file}")
        
        return synthesis_file
    
    def report(self):
        """최종 리포트 생성"""
        print("\n📊 토론 결과 리포트")
        print("=" * 60)
        
        for round_num in range(1, 4):
            print(f"\n=== Round {round_num} ===")
            for agent_name, _ in self.participants:
                result_file = os.path.join(self.debate_dir, f"{agent_name.lower()}_round{round_num}.md")
                if os.path.exists(result_file):
                    print(f"\n📄 {agent_name} ({agent_name.lower()}_round{round_num}.md):")
                    with open(result_file, 'r') as f:
                        content = f.read()
                        print(content[:200] + "..." if len(content) > 200 else content)
                else:
                    print(f"⚠️  {agent_name} Round {round_num} 결과 없음")
        
        synthesis_file = os.path.join(self.debate_dir, "synthesis.md")
        if os.path.exists(synthesis_file):
            print(f"\n=== Final Synthesis ===")
            with open(synthesis_file, 'r') as f:
                print(f.read())
        
        print(f"\n📁 전체 결과: {self.debate_dir}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 debate_orchestrator.py '<topic>'")
        print("Example: python3 debate_orchestrator.py 'AI가 의식을 가질 수 있는가?'")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    
    print("🎭 hih-debate 오케스트레이터 시작")
    print(f"주제: {topic}\n")
    
    orchestrator = DebateOrchestrator(topic=topic)
    
    # Step 1: 설정
    if not orchestrator.setup():
        sys.exit(1)
    
    # Step 2: 에이전트 시작 (pane 1: Claude, pane 3: GLM)
    print("\n🤖 에이전트 시작...")
    orchestrator.start_agent(1, "claude")
    orchestrator.start_agent(3, "glm")
    
    # Step 3~5: 라운드 진행
    orchestrator.run_round(1, [("Claude", None), ("GLM", None)])
    orchestrator.run_round(2, [("Claude", "glm_round1"), ("GLM", "claude_round1")])
    orchestrator.run_round(3, [("Claude", "glm_round2"), ("GLM", "claude_round2")])
    
    # Step 6: 시너지sis
    orchestrator.synthesis()
    
    # Step 7: 리포트
    orchestrator.report()
    
    print("\n✅ 토론 완료!")
    print(f"결과: {orchestrator.debate_dir}")


if __name__ == "__main__":
    main()
