import os
from typing import Optional

from postgrest._async.request_builder import AsyncQueryRequestBuilder
from pydantic import BaseModel
from supabase._async.client import AsyncClient as Client
from supabase._async.client import create_client

from app.utils.boolean_clause import (
    BooleanClause,
    apply_boolean_clause,
)


class DatabaseClient:
    _instance: Optional["DatabaseClient"] = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def _init(self):
        if self._instance is not self:
            raise RuntimeError("_init() should only be called through get_instance()")

        if not self._client:
            self._client = await create_client(
                supabase_url=os.environ["SUPABASE_URL"],
                supabase_key=os.environ["SUPABASE_SERVICE_KEY"],
            )

    @classmethod
    async def get_instance(cls) -> "DatabaseClient":
        if not cls._instance:
            client = cls()
            await client._init()

        if cls._instance is None:
            raise RuntimeError("DatabaseClient instance not initialized")
        return cls._instance

    async def post(self, table_name: str, data: BaseModel) -> list:
        if not self._client:
            raise TypeError("Database client is not initialized when executing a POST request")
        response = await self._client.table(table_name).insert(data.model_dump()).execute()
        return response.data

    async def get(
        self,
        table_name: str,
        column_names: list[str] = [],
        boolean_clause: Optional[BooleanClause] = None,
    ) -> list:
        if not self._client:
            raise TypeError("Database client is not initialized when executing a GET request")

        query = self._client.table(table_name).select(
            ", ".join(column_names) if column_names else "*"
        )
        query: AsyncQueryRequestBuilder = apply_boolean_clause(
            query=query, boolean_clause=boolean_clause
        )
        response = await query.execute()
        return response.data

    async def patch(
        self,
        table_name: str,
        data: dict,
        boolean_clause: Optional[BooleanClause] = None,
    ) -> list:
        if not self._client:
            raise TypeError("Database client is not initialized when executing a PATCH request")

        query = self._client.table(table_name).update(data)
        query = apply_boolean_clause(query=query, boolean_clause=boolean_clause)

        response = await query.execute()
        return response.data

    async def execute_rpc(self, rpc: str, params: Optional[dict] = None) -> list:
        """
        Executes a stored procedure call.
        """
        if not self._client:
            raise TypeError("Database client is not initialized when executing a RPC request")

        response = await self._client.rpc(rpc, params).execute()
        return response.data
