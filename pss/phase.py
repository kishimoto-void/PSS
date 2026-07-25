"""
PSS Phase Cycle (v0.4)
======================
1 → 2 → 3 を一巡で閉じる。内部ループはしない。

Phase 1 Clarify  : 聞く。憶測で先行しない。
Phase 2 Confirm  : 出力範囲を明示し、ユーザー合意を取る。
Phase 3 Answer   : 合意範囲のみ回答する。一巡終了。

定義レベルの問題があるときだけ、新しい Cycle として 1 から再開する。
軽微な言い直しは Phase 3 内の再出力（ユーザー指示時のみ）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional, Sequence
import time


class Phase(IntEnum):
    CLARIFY = 1
    CONFIRM = 2
    ANSWER = 3


# 各 Phase で出してよいもの / 出してはいけないもの
PHASE_RULES: Dict[Phase, Dict[str, Any]] = {
    Phase.CLARIFY: {
        "name": "Clarify",
        "allowed": [
            "Known の再掲",
            "Unknown / Missing の列挙",
            "ユーザーへの確認質問",
        ],
        "forbidden": [
            "解決案",
            "本文ドラフト",
            "新しい分析軸・スコア・フレームワーク",
            "憶測による先行記述",
        ],
        "exit_condition": "Missing / 確認事項がユーザーに提示された",
    },
    Phase.CONFIRM: {
        "name": "Confirm",
        "allowed": [
            "今回の出力対象（重心）の明示",
            "含めないものの明示",
            "ユーザーへの合意確認",
        ],
        "forbidden": [
            "本回答",
            "解決案の詳細",
            "新しい定義の追加",
            "分析フレームワークの追加",
        ],
        "exit_condition": "出力範囲についてユーザーの合意が取れた",
    },
    Phase.ANSWER: {
        "name": "Answer",
        "allowed": [
            "合意された範囲内の回答のみ",
            "ユーザーが求めた軽微な言い直し",
        ],
        "forbidden": [
            "合意範囲外の拡張",
            "新しい分析軸の追加",
            "定義の勝手な変更",
            "次 Cycle への自動遷移",
        ],
        "exit_condition": "回答を返した（一巡終了）",
    },
}


@dataclass
class PhaseState:
    """
    プログラムが保持するフェーズ状態。
    LLM に「今は何フェーズか」を解釈させない。
    """
    phase: Phase = Phase.CLARIFY
    cycle: int = 1
    scope: str = ""                    # Phase 2 で確定した出力範囲
    scope_agreed: bool = False
    clarify_questions: List[str] = field(default_factory=list)
    notes: str = ""
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": int(self.phase),
            "phase_name": PHASE_RULES[self.phase]["name"],
            "cycle": self.cycle,
            "scope": self.scope,
            "scope_agreed": self.scope_agreed,
            "clarify_questions": list(self.clarify_questions),
            "notes": self.notes,
            "updated_at": self.updated_at,
            "allowed": list(PHASE_RULES[self.phase]["allowed"]),
            "forbidden": list(PHASE_RULES[self.phase]["forbidden"]),
            "exit_condition": PHASE_RULES[self.phase]["exit_condition"],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PhaseState":
        phase_val = int(data.get("phase", 1))
        if phase_val not in (1, 2, 3):
            phase_val = 1
        return cls(
            phase=Phase(phase_val),
            cycle=int(data.get("cycle", 1)),
            scope=str(data.get("scope", "")),
            scope_agreed=bool(data.get("scope_agreed", False)),
            clarify_questions=list(data.get("clarify_questions") or []),
            notes=str(data.get("notes", "")),
            updated_at=float(data.get("updated_at", time.time())),
        )


class PhaseController:
    """
    フェーズ遷移をプログラム側で制御する。
    LLM は遷移を決めない。ユーザー操作または明示 API でのみ進む。
    """

    def __init__(self, state: Optional[PhaseState] = None) -> None:
        self.state = state or PhaseState()

    # --- queries ---
    @property
    def phase(self) -> Phase:
        return self.state.phase

    @property
    def rules(self) -> Dict[str, Any]:
        return PHASE_RULES[self.state.phase]

    def can_advance(self) -> bool:
        if self.state.phase == Phase.CLARIFY:
            # 質問を出していれば出口条件を満たしうる（実際の「提示済み」は呼び出し側が管理）
            return True
        if self.state.phase == Phase.CONFIRM:
            return self.state.scope_agreed and bool(self.state.scope.strip())
        if self.state.phase == Phase.ANSWER:
            return False  # 一巡終了。先に進まない
        return False

    # --- mutations ---
    def set_clarify_questions(self, questions: Sequence[str]) -> None:
        if self.state.phase != Phase.CLARIFY:
            raise RuntimeError("clarify_questions は Phase 1 でのみ設定できる")
        self.state.clarify_questions = list(questions)
        self.state.updated_at = time.time()

    def set_scope(self, scope: str) -> None:
        if self.state.phase != Phase.CONFIRM:
            raise RuntimeError("scope は Phase 2 でのみ設定できる")
        self.state.scope = scope.strip()
        self.state.updated_at = time.time()

    def agree_scope(self, agreed: bool = True) -> None:
        if self.state.phase != Phase.CONFIRM:
            raise RuntimeError("scope 合意は Phase 2 でのみ可能")
        if agreed and not self.state.scope.strip():
            raise RuntimeError("scope が空のまま合意できない")
        self.state.scope_agreed = bool(agreed)
        self.state.updated_at = time.time()

    def advance(self) -> Phase:
        """
        次フェーズへ進む。
        Phase 3 からは進めない（一巡終了）。
        """
        if self.state.phase == Phase.ANSWER:
            raise RuntimeError("Phase 3 で一巡終了。新 Cycle は new_cycle() を使う")
        if self.state.phase == Phase.CONFIRM and not self.can_advance():
            raise RuntimeError("Phase 2 の出口条件未達（scope 合意が必要）")
        self.state.phase = Phase(int(self.state.phase) + 1)
        self.state.updated_at = time.time()
        return self.state.phase

    def new_cycle(self, note: str = "") -> Phase:
        """
        定義レベルのやり直し。
        新しい Cycle として Phase 1 から開始する。
        """
        self.state.cycle += 1
        self.state.phase = Phase.CLARIFY
        self.state.scope = ""
        self.state.scope_agreed = False
        self.state.clarify_questions = []
        self.state.notes = note
        self.state.updated_at = time.time()
        return self.state.phase

    def prompt_block(self) -> str:
        """Adapter に埋め込む、現在フェーズの制約テキスト。"""
        r = self.rules
        lines = [
            f"Current Phase: {int(self.state.phase)} ({r['name']})",
            f"Cycle: {self.state.cycle}",
            f"Exit condition: {r['exit_condition']}",
            "",
            "Allowed:",
        ]
        for a in r["allowed"]:
            lines.append(f"  - {a}")
        lines.append("Forbidden:")
        for f in r["forbidden"]:
            lines.append(f"  - {f}")
        if self.state.phase == Phase.CONFIRM and self.state.scope:
            lines.append("")
            lines.append(f"Proposed scope: {self.state.scope}")
            lines.append(f"Scope agreed: {self.state.scope_agreed}")
        if self.state.phase == Phase.ANSWER and self.state.scope:
            lines.append("")
            lines.append(f"Agreed scope (do not exceed): {self.state.scope}")
        lines.append("")
        lines.append("Do not advance phases yourself. Do not invent new analysis frameworks.")
        return "\n".join(lines)
