import json
import uuid
import os
import logging
from datetime import datetime
from sqlmodel import Session, create_engine, select
from app import crud
from app.core.config import settings
from app.models import User, UserCreate, Patent, Company, InfringementAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)

    # Paths for data files
    base_path = os.path.dirname(os.path.abspath(__file__))
    patents_path = os.path.join(base_path, "../data/patents.json")
    companies_path = os.path.join(base_path, "../data/company_products.json")
    infringement_path = os.path.join(base_path, "../data/infringement_analysis.json")

    # Check if data files exist
    if (
        not os.path.exists(patents_path)
        or not os.path.exists(companies_path)
        or not os.path.exists(infringement_path)
    ):
        logger.warning("One or more data files do not exist. Skipping data load.")
        return

    try:
        # Load and parse the companies data
        with open(companies_path, "r", encoding="utf-8") as f:
            companies_data = json.load(f)

            if isinstance(companies_data, dict) and "companies" in companies_data:
                companies_data = companies_data["companies"]

            if not isinstance(companies_data, list):
                raise ValueError(
                    "Expected companies data to be a list of dictionaries."
                )

            # logger.info("Loaded companies data type: %s", type(companies_data))
            # logger.info(
            #     "First item in companies data: %s",
            #     companies_data[0] if companies_data else "No data found",
            # )

            for company in companies_data:
                if not isinstance(company, dict):
                    raise ValueError("Each company entry should be a dictionary.")

                company_name = company.get("name")
                if not company_name:
                    logger.warning(
                        "Skipping a company entry due to missing 'name' field."
                    )
                    continue

                products = company.get("products")
                if not products:
                    logger.warning(
                        "Skipping a company entry due to missing 'products' field."
                    )
                    continue

                new_company = Company(
                    id=uuid.uuid4(),
                    name=company_name,
                    products=products,
                )

                session.add(new_company)

            session.commit()  # Commit after adding all companies

        # Load and parse the patents data
        with open(patents_path, "r", encoding="utf-8") as f:
            patents_data = json.load(f)

            if not isinstance(patents_data, list):
                raise ValueError("Expected patents data to be a list of dictionaries.")

            for patent in patents_data:
                if not isinstance(patent, dict):
                    raise ValueError("Each patent entry should be a dictionary.")

                new_patent = Patent(
                    id=uuid.uuid4(),
                    publication_number=patent.get("publication_number") or "",
                    title=patent.get("title") or "",
                    abstract=patent.get("abstract"),
                    description=patent.get("description"),
                    priority_date=patent.get("priority_date"),
                    application_date=patent.get("application_date"),
                    grant_date=patent.get("grant_date"),
                    ai_summary=patent.get("ai_summary"),
                    raw_source_url=patent.get("raw_source_url"),
                    assignee=patent.get("assignee"),
                    inventors=patent.get("inventors"),
                    jurisdictions=patent.get("jurisdictions"),
                    classifications=patent.get("classifications"),
                    application_events=patent.get("application_events"),
                    citations=patent.get("citations"),
                    citations_non_patent=patent.get("citations_non_patent"),
                    image_urls=patent.get("image_urls"),
                    landscapes=patent.get("landscapes"),
                    attachment_urls=patent.get("attachment_urls"),
                    claims=patent.get("claims"),
                    provenance=patent.get("provenance"),
                    publish_date=patent.get("publish_date"),
                )

                if not new_patent.publication_number or not new_patent.title:
                    logger.warning(
                        "Skipping a patent entry due to missing required fields. Entry: %s",
                        {"id": patent.get("id"), "title": patent.get("title")},
                    )
                    continue

                session.add(new_patent)

            session.commit()  # Commit after adding all patents

        # Load and parse the infringement analysis data
        with open(infringement_path, "r", encoding="utf-8") as f:
            infringement_data = json.load(f)

        if not isinstance(infringement_data, list):
            raise ValueError(
                "Expected infringement analysis data to be a list of dictionaries."
            )

        for analysis in infringement_data:
            if not isinstance(analysis, dict):
                raise ValueError(
                    "Each infringement analysis entry should be a dictionary."
                )

            company_name = analysis.get("company_name")
            if not company_name:
                logger.warning(
                    "Skipping an infringement analysis entry due to missing 'company_name' field."
                )
                continue

            patent_id = analysis.get("patent_id")
            if not patent_id:
                logger.warning(
                    "Skipping an infringement analysis entry due to missing 'patent_id' field."
                )
                continue

            try:
                analysis_date = (
                    datetime.strptime(analysis["analysis_date"], "%Y-%m-%d")
                    if analysis.get("analysis_date")
                    else (
                        datetime.utcnow()
                        if analysis.get("analysis_date")
                        else datetime.utcnow()
                    )
                )

                new_analysis = InfringementAnalysis(
                    id=uuid.uuid4(),
                    company_name=company_name,
                    patent_id=patent_id,
                    top_infringing_products=analysis.get("top_infringing_products")
                    or [],
                    analysis_date=analysis_date,
                    overall_risk_assessment=analysis.get("overall_risk_assessment")
                    or "Not Assessed",
                    explanation=analysis.get("explanation") or "",
                )

                session.add(new_analysis)
            except ValueError as e:
                logger.error(
                    "Invalid date format in infringement analysis entry: %s", e
                )
                continue

        session.commit()  # Commit after adding all infringement analyses

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        session.rollback()
        logger.error("Error parsing JSON data: %s", e)
    except Exception as e:
        session.rollback()
        logger.error("An unexpected error occurred: %s", e)
