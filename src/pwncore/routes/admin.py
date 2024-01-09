import logging
from fastapi import APIRouter
from passlib.hash import bcrypt

from pwncore.models import (
    Team,
    Problem,
    Hint,
    User,
    PreEventSolvedProblem,
    PreEventProblem,
)
from pwncore.config import config
from pwncore.models.ctf import SolvedProblem

metadata = {
    "name": "admin",
    "description": "Admin routes (currently only running when development on)",
}

# TODO: Make this protected
router = APIRouter(prefix="/admin", tags=["admin"])

if config.development:
    logging.basicConfig(level=logging.INFO)


@router.get("/union")
async def calculate_team_coins():  # Inefficient, anyways will be used only once
    logging.info("Calculating team points form pre-event CTFs:")
    team_ids = await Team.filter().values_list("id", flat=True)
    for team_id in team_ids:
        member_tags = await User.filter(team_id=team_id).values_list("tag", flat=True)

        if not member_tags:
            return 0

        problems_solved = set(
            await PreEventSolvedProblem.filter(tag__in=member_tags).values_list(
                "problem_id", flat=True
            )
        )

        team = await Team.get(id=team_id)
        for ctf_id in problems_solved:
            team.coins += (await PreEventProblem.get(id=ctf_id)).points
        logging.info(f"{team.id}) {team.name}: {team.coins}")
        await team.save()


@router.get("/create")
async def init_db():
    await Problem.create(
        name="Invisible-Incursion",
        description="Chod de tujhe se na ho paye",
        author="Meetesh Saini",
        points=300,
        image_name="key:latest",
        image_config={"PortBindings": {"22/tcp": [{}]}},
    )
    await PreEventProblem.create(
        name="Static_test",
        description="Chod de tujhe se na ho paye",
        author="Meetesh Saini",
        points=20,
        flag="asd",
        url="lugvitc.org",
    )
    await PreEventProblem.create(
        name="New Static Test",
        description="AJJSBFISHDBFHSD",
        author="Meetesh Saini",
        points=21,
        flag="asdf",
        url="lugvitc.org",
    )
    await Problem.create(
        name="In-Plain-Sight",
        description="A curious image with hidden secrets?",
        author="KreativeThinker",
        points=300,
        image_name="key:latest",
        image_config={"PortBindings": {"22/tcp": [{}]}},
    )
    await Problem.create(
        name="GitGood",
        description="How to master the art of solving CTFs? Git good nub.",
        author="Aadivishnu and Shoubhit",
        points=300,
        image_name="test:latest",
        image_config={"PortBindings": {"22/tcp": [{}], "5000/tcp": [{}]}},
    )
    await Team.create(name="CID Squad", secret_hash=bcrypt.hash("veryverysecret"))
    await Team.create(
        name="Triple A battery", secret_hash=bcrypt.hash("chotiwali"), coins=20
    )
    await PreEventSolvedProblem.create(tag="23BCE1000", problem_id="1")
    await PreEventSolvedProblem.create(tag="23BRS1000", problem_id="1")
    # await PreEventSolvedProblem.create(
    #     tag="23BAI1000",
    #     problem_id="2"
    # )
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
    await Hint.create(order=0, problem_id=1, text="This is the first hint")
    await Hint.create(order=1, problem_id=1, text="This is the second hint")
    await Hint.create(order=2, problem_id=1, text="This is the third hint")
    await Hint.create(order=0, problem_id=2, text="This is the first hint")
    await Hint.create(order=1, problem_id=2, text="This is the second hint")
    await SolvedProblem.create(team_id=2, problem_id=1)
    await SolvedProblem.create(team_id=2, problem_id=2)
    await SolvedProblem.create(team_id=1, problem_id=2)
