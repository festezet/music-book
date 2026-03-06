"""
Workflow Sidebar - Visual workflow navigation for Music Book Generator
"""
import customtkinter as ctk
from typing import Callable, Optional


class WorkflowNode(ctk.CTkFrame):
    """Single workflow step node with circle indicator and label"""

    COLORS = {
        'pending': ('#6b7280', '#4b5563'),      # Gray
        'current': ('#2563eb', '#1d4ed8'),      # Blue
        'completed': ('#16a34a', '#15803d'),    # Green
    }

    def __init__(self, parent, step_number: int, step_name: str,
                 step_icon: str = "", callback: Optional[Callable] = None):
        super().__init__(parent, fg_color="transparent")

        self.step_number = step_number
        self.step_name = step_name
        self.step_icon = step_icon
        self.callback = callback
        self.state = 'pending'

        self._create_widgets()

    def _create_widgets(self):
        """Create node UI elements"""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", pady=5)

        # Circle button with step number
        self.circle = ctk.CTkButton(
            container,
            text=str(self.step_number),
            width=44,
            height=44,
            corner_radius=22,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._on_click,
            fg_color=self.COLORS['pending'][0],
            hover_color=self.COLORS['pending'][1]
        )
        self.circle.pack(side="left", padx=(10, 15))

        # Step info (icon + name)
        info_frame = ctk.CTkFrame(container, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        # Icon + Name
        text = f"{self.step_icon} {self.step_name}" if self.step_icon else self.step_name
        self.label = ctk.CTkLabel(
            info_frame,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color=("#6b7280", "#9ca3af"),
            anchor="w"
        )
        self.label.pack(fill="x")

        self._update_appearance()

    def set_state(self, state: str):
        """Update node state: pending, current, completed"""
        if state in self.COLORS:
            self.state = state
            self._update_appearance()

    def _update_appearance(self):
        """Update visual appearance based on state"""
        colors = self.COLORS.get(self.state, self.COLORS['pending'])

        self.circle.configure(fg_color=colors[0], hover_color=colors[1])

        if self.state == 'current':
            self.label.configure(
                text_color=("#1e293b", "#f1f5f9"),
                font=ctk.CTkFont(size=13, weight="bold")
            )
        elif self.state == 'completed':
            self.label.configure(
                text_color=("#16a34a", "#22c55e"),
                font=ctk.CTkFont(size=13)
            )
        else:
            self.label.configure(
                text_color=("#6b7280", "#9ca3af"),
                font=ctk.CTkFont(size=13)
            )

    def _on_click(self):
        """Handle click on node"""
        if self.callback:
            self.callback(self.step_number)


class ConnectorLine(ctk.CTkFrame):
    """Vertical line connecting workflow nodes"""

    def __init__(self, parent, completed: bool = False):
        super().__init__(
            parent,
            width=3,
            height=30,
            corner_radius=2,
            fg_color=("#16a34a", "#22c55e") if completed else ("#d1d5db", "#4b5563")
        )
        self.completed = completed

    def set_completed(self, completed: bool):
        """Update line color based on completion"""
        self.completed = completed
        self.configure(
            fg_color=("#16a34a", "#22c55e") if completed else ("#d1d5db", "#4b5563")
        )


class WorkflowSidebar(ctk.CTkFrame):
    """Vertical workflow sidebar with connected nodes for Music Book creation"""

    STEPS = [
        (1, "Selection", ""),
        (2, "Configuration", ""),
        (3, "Export", ""),
        (4, "Generation", ""),
    ]

    def __init__(self, parent, callback: Optional[Callable] = None, width: int = 180):
        super().__init__(parent, width=width, corner_radius=10)

        self.callback = callback
        self.nodes: dict[int, WorkflowNode] = {}
        self.connectors: list[ConnectorLine] = []
        self.current_step = 1

        self._create_widgets()

    def _create_widgets(self):
        """Create sidebar UI"""
        # Header
        header = ctk.CTkLabel(
            self,
            text="Workflow",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        header.pack(fill="x", padx=15, pady=(15, 10))

        # Separator
        sep = ctk.CTkFrame(self, height=2, fg_color=("#e5e7eb", "#374151"))
        sep.pack(fill="x", padx=15, pady=(0, 15))

        # Nodes container
        nodes_frame = ctk.CTkFrame(self, fg_color="transparent")
        nodes_frame.pack(fill="both", expand=True, padx=5)

        # Create nodes with connecting lines
        for i, (step_num, step_name, step_icon) in enumerate(self.STEPS):
            # Connecting line (except before first node)
            if i > 0:
                connector = ConnectorLine(nodes_frame)
                connector.pack(padx=(30, 0), anchor="w")
                self.connectors.append(connector)

            # Node
            node = WorkflowNode(nodes_frame, step_num, step_name, step_icon, self._on_node_click)
            node.pack(fill="x")
            self.nodes[step_num] = node

        # Set initial state
        self.set_active_step(1)

    def _on_node_click(self, step_number: int):
        """Handle node click - only allow navigation to completed or current steps"""
        if step_number <= self.current_step:
            if self.callback:
                self.callback(step_number)

    def set_active_step(self, step: int):
        """Highlight the active step, mark previous as completed"""
        self.current_step = step

        for num, node in self.nodes.items():
            if num < step:
                node.set_state('completed')
            elif num == step:
                node.set_state('current')
            else:
                node.set_state('pending')

        # Update connector lines
        for i, connector in enumerate(self.connectors):
            connector.set_completed(i < step - 1)

    def get_current_step(self) -> int:
        """Get current active step number"""
        return self.current_step
