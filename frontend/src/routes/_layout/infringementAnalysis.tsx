import {
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
  Heading,
  Input,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  VStack,
} from "@chakra-ui/react";
import { useState } from "react";
import { useMutation, UseMutationResult } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { InfringementService } from "../../client";
import Navbar from "../../components/Common/Navbar";

export const Route = createFileRoute("/_layout/infringementAnalysis")({
  component: InfringementAnalysis,
});

function InfringementsForm({ onSubmit }: { onSubmit: (patentId: string, companyName: string) => void }) {
  const [patentId, setPatentId] = useState("");
  const [companyName, setCompanyName] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(patentId, companyName);
  };

  return (
    <Box as="form" onSubmit={handleSubmit} mb={8}>
      <VStack spacing={4} align="stretch">
        <FormControl>
          <FormLabel>Patent ID</FormLabel>
          <Input
            value={patentId}
            onChange={(e) => setPatentId(e.target.value)}
            placeholder="Enter Patent ID"
            required
          />
        </FormControl>
        <FormControl>
          <FormLabel>Company Name</FormLabel>
          <Input
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="Enter Company Name"
            required
          />
        </FormControl>
        <Button type="submit" colorScheme="blue">
          Submit for Analysis
        </Button>
      </VStack>
    </Box>
  );
}

function InfringementsResult({ data, isLoading }: { data?: any; isLoading: boolean }) {
  if (isLoading) {
    return (
      <SkeletonText mt="4" noOfLines={4} spacing="4" />
    );
  }

  if (!data) {
    return null;
  }

  return (
    <TableContainer>
      <Table size={{ base: "sm", md: "md" }}>
        <Thead>
          <Tr>
            <Th>Product Name</Th>
            <Th>Infringement Likelihood</Th>
            <Th>Relevant Claims</Th>
          </Tr>
        </Thead>
        <Tbody>
          {data.top_infringing_products.map((product: any, index: number) => (
            <Tr key={index}>
              <Td>{product.product_name}</Td>
              <Td>{product.infringement_likelihood}</Td>
              <Td>{product.relevant_claims.join(", ")}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
}

function InfringementAnalysis() {
  const [result, setResult] = useState<any>(null);

  const mutation: UseMutationResult<any, Error, { patentId: string; companyName: string }> = useMutation(
    {
      mutationKey: ['checkInfringement'],
      mutationFn: ({ patentId, companyName }: { patentId: string; companyName: string }) =>
        InfringementService.checkInfringement({ patentId, companyName }),
      onSuccess: (data) => {
        setResult(data);
      },
    }
  );

  const handleSubmit = (patentId: string, companyName: string) => {
    mutation.mutate({ patentId, companyName });
  };

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12} mb={6}>
        Infringement Analysis
      </Heading>

      {/* <Navbar type={"Infringement"} /> */}

      <InfringementsForm onSubmit={handleSubmit} />
      <InfringementsResult data={result} isLoading={mutation.status === 'pending'} />
    </Container>
  );
}
