from app.models.api import ListRequest
from app.models.user import User, UserNextToken, UserUpdateData
from app.models.utils import SortOrder


class GETUsers(ListRequest):
    sort_field: User.SortField | None = None
    sort_order: SortOrder | None = None
    search_term: str | None = None

    @property
    def parsed_next_token(self) -> UserNextToken | None:

        if (self.sort_field or self.sort_order or self.search_term) and self.next_token:
            raise ValueError("Request should have either next_token or the filtering/sorting fields, not both")

        if self.next_token:
            return UserNextToken.model_validate_json(self.next_token)

        if self.sort_field or self.sort_order or self.search_term:
            return UserNextToken(
                skip=0,
                sort_field=self.sort_field,
                sort_order=self.sort_order,
                search_term=self.search_term,
            )

        return None


PATCHUser = UserUpdateData
