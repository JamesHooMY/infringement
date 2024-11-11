import {
  Container,
  Heading,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { CompanyService } from "../../client/index.ts";
import ActionsMenu from "../../components/Common/ActionsMenu.tsx";
import Navbar from "../../components/Common/Navbar.tsx";
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx";
import { z } from "zod"

const PER_PAGE = 5;

const companiesSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/companies")({
  component: Companies,
  validateSearch: (search) => companiesSearchSchema.parse(search),
});

function getCompaniesQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      CompanyService.readCompanies({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["companies", { page }],
  };
}

function CompaniesTable() {
  const queryClient = useQueryClient();
  const { page } = Route.useSearch();
  const navigate = useNavigate({ from: Route.fullPath });
  const setPage = (page: number) =>
    navigate({ search: (prev: { [key: string]: string }) => ({ ...prev, page }) });

  const {
    data: companies,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getCompaniesQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  });

  const hasNextPage = !isPlaceholderData && companies?.data.length === PER_PAGE;
  const hasPreviousPage = page > 1;

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getCompaniesQueryOptions({ page: page + 1 }));
    }
  }, [page, queryClient, hasNextPage]);

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(2).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {companies?.data.map((company) => (
                <Tr key={company.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{company.name}</Td>
                  <Td>
                    <ActionsMenu type={"Company"} value={company} />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          )}
        </Table>
      </TableContainer>
      <PaginationFooter
        page={page}
        onChangePage={setPage}
        hasNextPage={hasNextPage}
        hasPreviousPage={hasPreviousPage}
      />
    </>
  );
}

function Companies() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Company Management
      </Heading>

      {/* <Navbar type={"Company"} /> */}
      <CompaniesTable />
    </Container>
  );
}
