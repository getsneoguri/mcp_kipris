import os
import logging
from mcp.server.fastmcp import FastMCP
from mcp_kipris.kipris.tools import (
    ForeignPatentApplicantSearchTool,
    ForeignPatentApplicationNumberSearchTool,
    ForeignPatentFreeSearchTool,
    ForeignPatentInternationalApplicationNumberSearchTool,
    ForeignPatentInternationalOpenNumberSearchTool,
    KoreanPatentApplicantSearchTool,
    KoreanPatentApplicationNumberSearchTool,
    KoreanPatentDetailSearchTool,
    KoreanPatentFreeSearchTool,
    KoreanPatentRighterSearchTool,
    KoreanPatentSearchTool,
    KoreanPatentSummarySearchTool,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp-kipris")

api_key = os.getenv("KIPRIS_API_KEY")
if not api_key:
    raise ValueError("KIPRIS_API_KEY environment variable required.")

mcp = FastMCP("mcp-kipris")

tool_handlers = {}
for tool_class in [
    KoreanPatentApplicantSearchTool,
    KoreanPatentFreeSearchTool,
    KoreanPatentSearchTool,
    KoreanPatentRighterSearchTool,
    KoreanPatentApplicationNumberSearchTool,
    KoreanPatentSummarySearchTool,
    KoreanPatentDetailSearchTool,
    ForeignPatentApplicantSearchTool,
    ForeignPatentApplicationNumberSearchTool,
    ForeignPatentFreeSearchTool,
    ForeignPatentInternationalApplicationNumberSearchTool,
    ForeignPatentInternationalOpenNumberSearchTool,
]:
    instance = tool_class()
    tool_handlers[instance.name] = instance
    logger.info(f"Tool handler added: {instance.name}")


@mcp.tool()
async def patent_applicant_search(applicant: str, docs_count: int = 10, desc_sort: bool = True) -> str:
    """출원인명으로 국내 특허를 검색합니다."""
    return str(tool_handlers["patent_applicant_search"].run_tool({"applicant": applicant, "docs_count": docs_count, "desc_sort": desc_sort}))

@mcp.tool()
async def patent_keyword_search(word: str, docs_count: int = 10, desc_sort: bool = True) -> str:
    """키워드로 국내 특허를 검색합니다."""
    return str(tool_handlers["patent_keyword_search"].run_tool({"word": word, "docs_count": docs_count, "desc_sort": desc_sort}))

@mcp.tool()
async def patent_search(application_number: str) -> str:
    """출원번호로 국내 특허를 검색합니다."""
    return str(tool_handlers["patent_search"].run_tool({"application_number": application_number}))

@mcp.tool()
async def patent_righter_search(righter: str, docs_count: int = 10, desc_sort: bool = True) -> str:
    """권리자명으로 국내 특허를 검색합니다."""
    return str(tool_handlers["patent_righter_search"].run_tool({"righter": righter, "docs_count": docs_count, "desc_sort": desc_sort}))

@mcp.tool()
async def patent_application_number_search(application_number: str) -> str:
    """출원번호로 특허 정보를 조회합니다."""
    return str(tool_handlers["patent_application_number_search"].run_tool({"application_number": application_number}))

@mcp.tool()
async def patent_summary_search(application_number: str) -> str:
    """출원번호로 특허 요약 정보를 조회합니다."""
    return str(tool_handlers["patent_summary_search"].run_tool({"application_number": application_number}))

@mcp.tool()
async def patent_detail_search(application_number: str) -> str:
    """출원번호로 특허 상세 정보를 조회합니다."""
    return str(tool_handlers["patent_detail_search"].run_tool({"application_number": application_number}))

@mcp.tool()
async def foreign_patent_applicant_search(applicant: str, nation: str = "US", docs_count: int = 10) -> str:
    """출원인명으로 해외 특허를 검색합니다. nation: US/EP/JP/CN/WO"""
    return str(tool_handlers["foreign_patent_applicant_search"].run_tool({"applicant": applicant, "nation": nation, "docs_count": docs_count}))

@mcp.tool()
async def foreign_patent_free_search(word: str, nation: str = "US", docs_count: int = 10) -> str:
    """키워드로 해외 특허를 검색합니다. nation: US/EP/JP/CN/WO"""
    return str(tool_handlers["foreign_patent_free_search"].run_tool({"word": word, "nation": nation, "docs_count": docs_count}))

@mcp.tool()
async def foreign_patent_application_number_search(application_number: str, nation: str = "US") -> str:
    """출원번호로 해외 특허를 조회합니다."""
    return str(tool_handlers["foreign_patent_application_number_search"].run_tool({"application_number": application_number, "nation": nation}))

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=6274, path="/mcp")
