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
import { PatentService } from "../../client/index.ts";
import ActionsMenu from "../../components/Common/ActionsMenu.tsx";
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx";
import { z } from "zod"

const PER_PAGE = 5;

const patentsSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/patents")({
  component: Patents,
  validateSearch: (search) => patentsSearchSchema.parse(search),
});

function getPatentsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      PatentService.readPatents({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["patents", { page }],
  };
}

function PatentsTable() {
  const queryClient = useQueryClient();
  const { page } = Route.useSearch();
  const navigate = useNavigate({ from: Route.fullPath });
  const setPage = (page: number) =>
    navigate({ search: (prev: { [key: string]: string }) => ({ ...prev, page }) });

  const {
    data: patents,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getPatentsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  });

  const hasNextPage = !isPlaceholderData && patents?.data.length === PER_PAGE;
  const hasPreviousPage = page > 1;

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getPatentsQueryOptions({ page: page + 1 }));
    }
  }, [page, queryClient, hasNextPage]);

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>Publication Number</Th>
              <Th>Title</Th>
              <Th>Assignee</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(3).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {patents?.data.map((patent) => (
                <Tr key={patent.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{patent.publication_number}</Td>
                  <Td isTruncated maxWidth="150px">
                    {patent.title}
                  </Td>
                  <Td>{patent.assignee}</Td>
                  <Td>
                    <ActionsMenu type={"Patent"} value={patent} />
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

function Patents() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Patent Management
      </Heading>

      {/* <Navbar type={"Patent"} /> */}
      <PatentsTable />
    </Container>
  );
}
