# General Manager 设定调整指令示例

这不是一次性的运行时指令，而是长期设定调整任务。  
目标是修改 General Manager 的长期角色设定文件，使其默认行为从“收到任务后容易进入多智能体调度”改为“收到任务后先进行任务处理判断”。

应修改文件：
- agents/general-manager/PROMPT.md
- agents/general-manager/soul.md
- agents/general-manager/memory.md

必要时同步更新：
- system/SYSTEM_SPEC.md
- system/AGENTS.md
- system/ORCHESTRATION.md
- system/MESSAGE_ROUTING.md
