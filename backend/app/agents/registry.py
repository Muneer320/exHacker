
import structlog

from app.agents.base import BaseAgent

logger = structlog.get_logger()


class AgentRegistry:
    _agents: dict[str, BaseAgent] = {}

    @classmethod
    def register(cls, agent: BaseAgent) -> None:
        if agent.name in cls._agents:
            logger.warning("agent_overwritten", name=agent.name)
        cls._agents[agent.name] = agent
        logger.info("agent_registered", name=agent.name, critical=agent.critical)

    @classmethod
    def get(cls, name: str) -> BaseAgent | None:
        return cls._agents.get(name)

    @classmethod
    def get_all(cls) -> dict[str, BaseAgent]:
        return dict(cls._agents)

    @classmethod
    def get_critical_agents(cls) -> list[BaseAgent]:
        return [a for a in cls._agents.values() if a.critical]

    @classmethod
    def get_non_critical_agents(cls) -> list[BaseAgent]:
        return [a for a in cls._agents.values() if not a.critical]

    @classmethod
    def get_by_names(cls, names: list[str]) -> list[BaseAgent]:
        agents: list[BaseAgent] = []
        for name in names:
            agent = cls.get(name)
            if agent:
                agents.append(agent)
        return agents

    @classmethod
    def clear(cls) -> None:
        cls._agents.clear()
        logger.info("agent_registry_cleared")
