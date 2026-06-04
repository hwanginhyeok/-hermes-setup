#!/usr/bin/env python3
"""PM-Bot 추가 명령 핸들러 템플릿

새 명령 추가 시 이 파일을 복사한 후 cmd_newcommand 함수를 수정하세요.

사용법:
1. 이 파일을 bot/extra_handlers.py로 저장
2. pm_bot.py에 import 추가: from bot.extra_handlers import cmd_newcommand
3. main() 함수에 핸들러 등록: app.add_handler(CommandHandler("newcommand", cmd_newcommand))
"""

import re
from datetime import datetime
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

# PM 관련 설정 - pm_bot.py에서 PM_DIR을 참조하거나 별도로 설정
PM_DIR = Path(__file__).resolve().parent.parent


async def cmd_add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """태스크 추가: /add {프로젝트} {태스크명} [우선순위]"""
    args = ctx.args
    if len(args) < 2:
        await update.message.reply_text("사용법: /add {프로젝트} {태스크명} [우선순위]\n예: /add bea 네이버 발행 로직 개발 P1")
        return
    
    project = args[0]
    task_name = " ".join(args[1:-1]) if len(args) > 2 else args[1]
    priority = args[-1].upper() if args[-1].upper() in ["P1", "P2", "P3"] else "P2"
    
    # 프로젝트 경로 확인
    project_paths = {
        "bea": Path.home() / "be-a-studio",
        "stock": Path.home() / "stock",
        "insung": Path.home() / "insung_blog",
        "music": Path.home() / "music-lab",
        "hermes": Path.home() / "project-manager",
    }
    
    if project not in project_paths:
        await update.message.reply_text(f"❌ 알 수 없는 프로젝트: {project}\n가능한 프로젝트: bea, stock, insung, music, hermes")
        return
    
    project_dir = project_paths[project]
    prepared_task = project_dir / "PREPARED_TASK.md"
    
    if not prepared_task.exists():
        await update.message.reply_text(f"❌ {project}에 PREPARED_TASK.md 없음")
        return
    
    # ID 생성 (기존 ID +1)
    existing_content = prepared_task.read_text()
    existing_ids = re.findall(r'\|\s*(\d+)\s*\|', existing_content)
    new_id = max([int(id) for id in existing_ids] + [0]) + 1
    
    # 날짜
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 태스크 추가
    new_task = f"| {new_id} | {task_name} | {priority} | - | {today} |\n"
    
    # 파일에 추가
    if existing_content.strip():
        new_content = existing_content + "\n" + new_task
    else:
        new_content = new_task
    
    prepared_task.write_text(new_content)
    
    await update.message.reply_text(f"✅ {project}에 태스크 추가 완료\nID: {new_id}\n태스크: {task_name}\n우선순위: {priority}")


async def cmd_auto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """자동화 작업 트리거: /auto {프로젝트} {작업 설명}"""
    args = ctx.args
    
    # /auto list 체크
    if len(args) == 1 and args[0] == "list":
        automation_dir = PM_DIR / "automations"
        if not automation_dir.exists():
            await update.message.reply_text("📭 등록된 자동화 없음")
            return
        
        files = list(automation_dir.glob("*.md"))
        if not files:
            await update.message.reply_text("📭 등록된 자동화 없음")
            return
        
        summary = ["📋 등록된 자동화\n"]
        for f in sorted(files, reverse=True)[:10]:
            summary.append(f"\n• {f.name}")
        
        await update.message.reply_text("\n".join(summary))
        return
    
    if len(args) < 2:
        await update.message.reply_text("사용법: /auto {프로젝트} {작업 설명}\n예: /auto bea 1시간마다 태스크 체크\n\n등록된 자동화 목록: /auto list")
        return
    
    project = args[0]
    description = " ".join(args[1:])
    
    # 자동화 등록
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    automation_file = PM_DIR / "automations" / f"{project}_{timestamp}.md"
    automation_file.parent.mkdir(parents=True, exist_ok=True)
    
    automation_content = f"""# 자동화 — {project}

## 작업 설명
{description}

## 생성일
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    automation_file.write_text(automation_content)
    
    await update.message.reply_text(f"✅ 자동화 등록 완료\n프로젝트: {project}\n작업: {description}\n\ncron 등록이 필요합니다.")


# ============================================================
# 새로운 명령 추가 시 아래 함수를 복사해서 수정하세요
# ============================================================

async def cmd_newcommand(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """새로운 명령 설명
    
    사용법: /newcommand {인자1} {인자2}
    예: /newcommand foo bar
    """
    # 권한 체크 (필요 시)
    # if not _authorized(update):
    #     return
    
    args = ctx.args
    
    # 인자 검증
    if len(args) < 1:
        await update.message.reply_text("사용법: /newcommand {인자1}\n예: /newcommand foo")
        return
    
    # 로직 구현
    # result = do_something(args[0])
    
    # 응답 전송
    await update.message.reply_text(f"✅ 명령 실행 완료\n결과: {args[0]}")