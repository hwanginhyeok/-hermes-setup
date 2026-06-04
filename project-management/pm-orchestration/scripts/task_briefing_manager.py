#!/usr/bin/env python3
"""task 브리핑 파일 관리 유틸리티.

전달용 (/tmp/) + 보관용 (task_briefings/) 이중 저장.
"""
import shutil
from datetime import datetime
from pathlib import Path


def create_task_briefing(
    project: str,
    subtask: str,
    content: str,
) -> tuple[str, str]:
    """전달용 + 보관용 파일 생성.

    Args:
        project: 프로젝트명 (bea, stock, insung, music, hermes)
        subtask: 서브태스크명 (A, B, C)
        content: 브리핑 내용

    Returns:
        (전달용 경로, 보관용 경로)
    """
    # 전달용 (/tmp/)
    tmp_path = f"/tmp/{project}_task_{subtask}.md"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)

    # 보관용 (task_briefings/)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_dir = Path.home() / "project-manager" / "content_queue" / "task_briefings" / project
    history_dir.mkdir(parents=True, exist_ok=True)

    history_path = history_dir / f"task_{timestamp}_{subtask}.md"
    shutil.copy2(tmp_path, history_path)

    return tmp_path, str(history_path)


def deliver_to_pane(session: str, pane: str, task_file: str) -> None:
    """tmux pane에 브리핑 전달.

    Args:
        session: tmux 세션명 (bea, stock, insung, music, hermes)
        pane: pane 번호 (1.2, 1.3, ...)
        task_file: 전달용 파일 경로
    """
    import subprocess

    cmd = f"tmux send-keys -t {session}:{pane} 'cat {task_file}' Enter"
    subprocess.run(cmd, shell=True, check=True)


if __name__ == "__main__":
    # 테스트
    content = """## 서브태스크 테스트

### 목표
task 브리핑 관리 유틸리티 테스트

### 완료 조건
- [ ] 파일 생성
- [ ] pane 전달
"""

    tmp_path, history_path = create_task_briefing("bea", "test", content)
    print(f"전달용: {tmp_path}")
    print(f"보관용: {history_path}")