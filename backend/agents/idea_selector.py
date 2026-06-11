def idea_selector_node(state):

    ranked_ideas = state["ranked_ideas"]

    return {
        "selected_idea": ranked_ideas[0]
    }