import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()


def generate_ppt(input_str: str):
    # logger.info("Inside the generate_ppt")
    url = "https://public-api.gamma.app/v0.2/generations"
    prompt = f"""### You have to generate a professional grade pptx on the content {input_str}\n\n # Analyze the content very carefully and generate a ppt."""
    payload = {
        "inputText": prompt,
        "textMode": "generate",
        "format": "presentation",
        "numCards": 7,
        "cardSplit": "auto",
        "textOptions": {"amount": "medium", "language": "en"},
        "imageOptions": {"source": "aiGenerated"},
        "exportAs": "pptx",
        "sharingOptions": {"workspaceAccess": "fullAccess", "externalAccess": "edit"},
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-API-KEY": os.getenv("GAMMA_API_KEY"),
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        # logger.info(f"Generated input: {response.text}")
        return response.json()
    except Exception as e:
        # logger.error(f"{e.__class__.__name__}: {str(e)}")
        raise e


prompt = """
TEAM 3 – LearnIQ
Use Case: Powering Continuous Upskilling Through Personalized Learning for ConceptVines Workforce
Background
As ConceptVines expands into the US market, the company must rapidly strengthen internal capabilities - especially in AI, engineering, product, and delivery.
However, the current learning workflow is fragmented:
Employees don’t know what to learn next
Learning paths differ widely between individuals
Content discovery is random and overwhelming
No structured visibility into learning progress
Internal knowledge-sharing is low
Weekly learning communication is manual and inconsistent
LearnIQ must evolve into a smart, agent-driven learning ecosystem that supports continuous upskilling at scale.

Business Problem — Workforce Readiness Needs Closing Learning Gaps
ConceptVines faces three major gaps that prevent efficient skill development:
1. Learning Path Gap
Learners often choose content based on:
Random YouTube videos
Unstructured recommendations
Peer suggestions
This results in:
Slow upskilling
Wrong learning priorities
No standard growth roadmap
2. Content Discovery Gap
Even motivated learners struggle because:
They cannot filter relevant content
They don’t know which content fits their skill track
They cannot validate quality or relevance
Internal LMS content is underutilized because it lacks personalization.
3. Engagement & Visibility Gap
Leaders and learners lack:
Weekly updates
Clear progress view
Motivation loops
Peer-driven learning
Manual newsletters or Slack posts are not scalable.
LearnIQ must address all three gaps to support ConceptVines’ capability-building strategy.

Hackathon Mission
Build a Personalised Learning Intelligence Framework inside LearnIQ that empowers learners to:
Receive tailored learning paths using the Personalised Learning Path Generator Agent
Discover curated content recommendations via the Content Discovery Recommendation Agent
Stay engaged through weekly auto-generated learning digests using the Newsletter Engine Agent
This becomes the skill development engine enabling ConceptVines to scale with a future-ready workforce.

Expected End-to-End Workflow
STEP 1 – Personalized Learning Path Generator Agent
LearnIQ must generate structured learning paths for each individual employee.
What the agent must do:
Accept learner role, goals, interests, and primary/secondary tracks
Generate a sequenced roadmap of modules
Provide milestone-based progression
Use ontology to map skills → modules → assessments
Estimate completion time
Justify recommendations using embeddings & prior performance
Expected Output:
| Module | Skill | Difficulty | Sequence | Reasoning | ETA |
This removes the Learning Path Gap.

STEP 2 – Content Discovery Recommendation Agent
Once the path is created, learners must receive highly relevant content.
What the agent must do:
Recommend videos, articles, courses, documents, code repos
Provide “Why this was recommended” explanation
Rank based on difficulty, relevance, recency
Show multiple content formats
Tag with ontology-based skill nodes
Expected Output:
| Content | Type | Skill Tag | Difficulty | Source | Reason |
This removes the Content Discovery Gap.

STEP 3 – Newsletter Engine for Learning
The agent must generate weekly learning digests for each individual and track group.
What the agent must include:
Personal progress summary
Highlighted content for next week
Achievements or badges
Team/track-level learning highlights
User-contributed learning notes
Motivational leaderboard snippets
Expected Output:
A ready-to-send weekly newsletter that feels personalized and insightful.
This removes the Engagement & Visibility Gap.

STEP 4 – Frontend Requirements
Team 4 must implement UI screens aligned with the backlog:
1. Personalized Path UI
Visual roadmap
Module progression
Milestones
2. Content Explorer UI
Recommendation cards
Filters
“Why recommended” overlay
3. Newsletter Builder UI
Preview
Edit
Schedule

4. Admin Controls
Adjust recommendation weights
Manage tracks & skill
View learner engagement metrics

Success Criteria
Learners receive personalized learning paths in seconds
Content feels curated, relevant, and high quality
Weekly newsletters keep learners engaged
Leaders get visibility into learning progress
Internal learning adoption increases significantly
ConceptVines develops AI-ready, project-ready talent faster
LearnIQ becomes the center of continuous capability building
In slide 1 you need to talk about what is learn iq
In slide 2 you need to talk about the ontology used in learn iq
In slide 3, you talk about the agents in learn iq
In slide 4, you talk about langfuse for evals and prompt versioning
generate a ppt, which should cover the main entities:
ontology
langfuse
agents
frontend
backend
database

There MUST be atleast
"""


def download_ppt(res_dict: dict):
    # logger.info("Inside the download ppt function")
    try:
        if not isinstance(res_dict, dict):
            # logger.warning("Given parameter named res_dict is not a dict")
            return "Given parameter named res_dict is not a dict"

        generation_id = res_dict.get("generationId")
        if not generation_id:
            raise ValueError("generationId not found in response dictionary")

        # logger.info(f"generationId: {generation_id}")
        print(f"generationId: {generation_id}")
        url = f"https://public-api.gamma.app/v0.2/generations/{generation_id}"
        # logger.info(url)

        headers = {
            "accept": "application/json",
            "X-API-KEY": os.getenv("GAMMA_API_KEY"),
        }

        export_url = None
        max_retries = 20  # wait up to ~100s
        for attempt in range(max_retries):
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            res = response.json()
            print(f"Attempt {attempt + 1}: {res}")

            export_url = res.get("exportUrl")
            if export_url:
                print(f"Got exportUrl: {export_url}")
                break

            sleep_time = min(2**attempt, 30)  # exponential backoff, max 30s
            print(f"Still pending. Sleeping {sleep_time}s before retry...")
            time.sleep(sleep_time)

        if not export_url:
            raise TimeoutError("exportUrl not available after multiple retries")

        ppt_response = requests.get(export_url, stream=True)
        ppt_response.raise_for_status()

        # Download the file locally
        filename = f"Presentation_{generation_id}.pptx"
        with open(filename, "wb") as f:
            for chunk in ppt_response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Successfully downloaded PPT as {filename}")
        return filename

    except Exception as e:
        # logger.error(f"{e.__class__.__name__}: {str(e)}")
        raise e


if __name__ == "__main__":
    res = generate_ppt(prompt)
    print(res)
    gen = download_ppt(res)
    print(gen)
