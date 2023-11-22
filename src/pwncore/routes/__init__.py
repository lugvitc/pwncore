from fastapi import APIRouter

from pwncore.routes import ctf, team
from pwncore.config import config
from pwncore.models import Problem, Team, Container, Hint, User

# Main router (all routes go under /api)
router = APIRouter(prefix="/api")


@router.get("/create")
async def init_db():
    if config.development:
        await Problem.create(
            name="Invisible-Incursion",
            description="Chod de tujhe se na ho paye",
            author="Meetesh Saini",
            points=300,
            image_name="key:latest",
            image_config={"PortBindings": {"22/tcp": [{}]}},
        )
        await Problem.create(
            name="In-Plain-Sight",
            description="A curious image with hidden secrets?",
            author="KreativeThinker",
            points=300,
            image_name="key:latest",
            image_config={"PortBindings": {"22/tcp": [{}]}},
        )
        await Team.create(name="CID Squad", secret_hash="veryverysecret")
        await Team.create(name="Triple A battery", secret_hash="chotiwali")
        await User.create(
            tag="23BRS1000",
            name="abc",
            team_id=2,
            phone_num=1111111111,
            email="email1@xyz.org",
        )
        await User.create(
            tag="23BCE1000",
            name="def",
            team_id=2,
            phone_num=2222222222,
            email="email1@xyz.org",
        )
        await User.create(
            tag="23BAI1000",
            name="ghi",
            team_id=2,
            phone_num=3333333333,
            email="email1@xyz.org",
        )
        await User.create(
            tag="23BRS2000",
            name="ABC",
            team_id=1,
            phone_num=4444444444,
            email="email1@xyz.org",
        )
        await User.create(
            tag="23BCE2000",
            name="DEF",
            team_id=1,
            phone_num=5555555555,
            email="email1@xyz.org",
        )
        await User.create(
            tag="23BAI2000",
            name="GHI",
            team_id=1,
            phone_num=6666666666,
            email="email1@xyz.org",
        )
        await Container.create(
            docker_id="letsjustsay1",
            flag="pwncore{flag_1}",
            problem_id=1,
            team_id=1,
        )
        await Container.create(
            docker_id="letsjustsay2",
            flag="pwncore{flag_2}",
            problem_id=2,
            team_id=1,
        )
        await Container.create(
            docker_id="letsjustsay3",
            flag="pwncore{farmers}",
            problem_id=2,
            team_id=2,
        )
        await Hint.create(order=0, problem_id=1, text="This is the first hint")
        await Hint.create(order=1, problem_id=1, text="This is the second hint")
        await Hint.create(order=2, problem_id=1, text="This is the third hint")
        await Hint.create(order=0, problem_id=2, text="This is the first hint")
        await Hint.create(order=1, problem_id=2, text="This is the second hint")


# Include all the subroutes
router.include_router(ctf.router)
router.include_router(team.router)
