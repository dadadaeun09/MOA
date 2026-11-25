"""MOA - 흩어진 일정을 한곳에 모아, 우선순위대로 보여주는 일정 관리 앱"""
from datetime import date

import customtkinter as ctk

from core import Task, load_tasks, save_tasks, sort_tasks

ctk.set_appearance_mode("system")

# (라이트, 다크) 색상 쌍
BG = ("#F5F6FA", "#111218")
CARD = ("#FFFFFF", "#1C1E27")
TEXT = ("#1A1B22", "#F1F2F6")
SUB = ("#80848F", "#8B8F9C")
ACCENT = "#6366F1"
ACCENT_HOVER = "#4F52D9"
HOT = "#F43F5E"
MID = "#F59E0B"
LOW = "#94A3B8"


def badge_color(score: int) -> str:
    return HOT if score >= 8 else MID if score >= 6 else LOW


def dday_text(days: int) -> str:
    if days == 0:
        return "D-DAY"
    return f"D-{days}" if days > 0 else f"D+{-days} 지남"


class MoaApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG)
        self.title("MOA")
        self.geometry("560x720")
        self.minsize(480, 600)

        self.tasks = load_tasks()

        # 헤더
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(28, 4))
        ctk.CTkLabel(header, text="MOA", font=("Helvetica", 32, "bold"),
                     text_color=ACCENT).pack(anchor="w")
        ctk.CTkLabel(header, text="흩어진 일정을 한곳에 모아요",
                     font=("Helvetica", 13), text_color=SUB).pack(anchor="w")

        # 입력 카드
        form = ctk.CTkFrame(self, fg_color=CARD, corner_radius=20)
        form.pack(fill="x", padx=24, pady=16)

        self.title_entry = ctk.CTkEntry(
            form, placeholder_text="무슨 일정인가요?", height=42,
            corner_radius=12, border_width=0, fg_color=BG)
        self.title_entry.pack(fill="x", padx=16, pady=(16, 8))

        row = ctk.CTkFrame(form, fg_color="transparent")
        row.pack(fill="x", padx=16)
        self.due_entry = ctk.CTkEntry(
            row, placeholder_text="마감일 YYYY-MM-DD", width=170, height=38,
            corner_radius=12, border_width=0, fg_color=BG)
        self.due_entry.pack(side="left")
        self.importance = ctk.CTkSegmentedButton(
            row, values=["1", "2", "3", "4", "5"], height=38,
            selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
            unselected_color=BG, unselected_hover_color=BG, text_color=TEXT)
        self.importance.set("3")
        self.importance.pack(side="right")
        ctk.CTkLabel(row, text="중요도", text_color=SUB,
                     font=("Helvetica", 12)).pack(side="right", padx=8)

        self.msg = ctk.CTkLabel(form, text="", text_color=HOT, font=("Helvetica", 12))
        self.msg.pack(anchor="w", padx=20, pady=(6, 0))

        ctk.CTkButton(
            form, text="일정 추가", height=42, corner_radius=12,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            font=("Helvetica", 14, "bold"), command=self.add_task,
        ).pack(fill="x", padx=16, pady=(4, 16))

        self.bind("<Return>", lambda _e: self.add_task())

        # 일정 리스트
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.refresh()

    # ---- 동작 ----
    def add_task(self):
        title = self.title_entry.get().strip()
        due = self.due_entry.get().strip()
        if not title:
            return self.msg.configure(text="일정 이름을 입력해 주세요.")
        try:
            date.fromisoformat(due)
        except ValueError:
            return self.msg.configure(text="마감일을 YYYY-MM-DD 형식으로 입력해 주세요.")

        self.tasks.append(Task(title, due, int(self.importance.get())))
        save_tasks(self.tasks)
        self.title_entry.delete(0, "end")
        self.due_entry.delete(0, "end")
        self.msg.configure(text="")
        self.refresh()

    def toggle(self, task: Task):
        task.done = not task.done
        save_tasks(self.tasks)
        self.refresh()

    def remove(self, task: Task):
        self.tasks = [t for t in self.tasks if t.id != task.id]
        save_tasks(self.tasks)
        self.refresh()

    # ---- 화면 ----
    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.tasks:
            ctk.CTkLabel(self.list_frame, text="아직 일정이 없어요.\n첫 일정을 추가해 보세요 ✨",
                         text_color=SUB, font=("Helvetica", 14)).pack(pady=60)
            return

        today = date.today()
        for task in sort_tasks(self.tasks, today):
            self.make_card(task, today)

    def make_card(self, task: Task, today: date):
        score = task.priority(today)
        card = ctk.CTkFrame(self.list_frame, fg_color=CARD, corner_radius=16)
        card.pack(fill="x", padx=8, pady=5)

        ctk.CTkLabel(
            card, text=str(score), width=44, height=44, corner_radius=12,
            fg_color=LOW if task.done else badge_color(score),
            text_color="white", font=("Helvetica", 18, "bold"),
        ).pack(side="left", padx=14, pady=14)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            info, text=task.title, anchor="w",
            text_color=SUB if task.done else TEXT,
            font=("Helvetica", 15, "bold", "overstrike") if task.done
            else ("Helvetica", 15, "bold"),
        ).pack(fill="x")
        ctk.CTkLabel(
            info, anchor="w", text_color=SUB, font=("Helvetica", 12),
            text=f"{dday_text(task.days_left(today))} · {task.due} · 중요도 {task.importance}",
        ).pack(fill="x")

        ctk.CTkButton(card, text="✕", width=32, height=32, corner_radius=10,
                      fg_color="transparent", text_color=SUB,
                      hover_color=BG, command=lambda: self.remove(task)
                      ).pack(side="right", padx=(0, 10))
        ctk.CTkCheckBox(card, text="", width=24, checkbox_width=24, checkbox_height=24,
                        corner_radius=8, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                        command=lambda: self.toggle(task),
                        ).pack(side="right", padx=4)
        # 체크박스 초기 상태 반영
        if task.done:
            card.winfo_children()[-1].select()


if __name__ == "__main__":
    MoaApp().mainloop()
