from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.ai.copilot import generate_sql, format_response


async def answer_question(db: AsyncSession, question: str) -> dict:
    sql_query = await generate_sql(question)

    if not sql_query or sql_query.strip().upper().startswith(("DROP", "INSERT", "UPDATE", "DELETE", "ALTER", "TRUNCATE", "CREATE")):
        return {"answer": "I couldn't process that question. Try asking about vendors, risk, or certifications.", "sources": []}

    try:
        result = await db.execute(text(sql_query))
        rows = result.fetchmany(50)
        columns = result.keys()

        data = [dict(zip(columns, row)) for row in rows]
        answer = await format_response(question, data, columns)

        return {
            "answer": answer,
            "sources": [f"Query: {sql_query[:200]}..."],
        }
    except Exception as e:
        return {
            "answer": "I encountered an error while looking up that information. Please try rephrasing your question.",
            "sources": [],
        }
