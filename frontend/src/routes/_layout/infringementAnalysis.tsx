import {
  Box,
  Button,
  Container,
  Divider,
  FormControl,
  FormLabel,
  Heading,
  Progress,
  Select,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  VStack,
  useColorModeValue,
} from "@chakra-ui/react";
import { useState } from "react";
import { useQuery, useMutation, UseMutationResult } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { InfringementService, PatentService, CompanyService } from "../../client";

export const Route = createFileRoute("/_layout/infringementAnalysis")({
  component: InfringementAnalysis,
});

function InfringementsForm({ onSubmit }: { onSubmit: (patentId: string, companyName: string) => void }) {
  const [patentId, setPatentId] = useState("");
  const [companyName, setCompanyName] = useState("");

  // Fetch all patents and companies
  const { data: patents, isLoading: loadingPatents } = useQuery({
    queryKey: ["patents"],
    queryFn: () => PatentService.readPatents({ limit: 100 })
  });
  const { data: companies, isLoading: loadingCompanies } = useQuery({
    queryKey: ["companies"],
    queryFn: () => CompanyService.readCompanies({ limit: 100 })
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(patentId, companyName);
  };

  return (
    <Box as="form" onSubmit={handleSubmit} mb={8}>
      <VStack spacing={4} align="stretch">
        <FormControl>
          <FormLabel>Patent ID</FormLabel>
          {loadingPatents ? (
            <SkeletonText noOfLines={1} />
          ) : (
            <Select
              placeholder="Select a Patent"
              value={patentId}
              onChange={(e) => setPatentId(e.target.value)}
              required
              width={{ base: "100%", md: "50%" }} // Adjusted width
            >
              {patents?.data.map((patent: any) => (
                <option key={patent.id} value={patent.publication_number}>
                  {`${patent.publication_number} - ${patent.title}`}
                </option>
              ))}
            </Select>
          )}
        </FormControl>
        <FormControl>
          <FormLabel>Company Name</FormLabel>
          {loadingCompanies ? (
            <SkeletonText noOfLines={1} />
          ) : (
            <Select
              placeholder="Select a Company"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              required
              width={{ base: "100%", md: "50%" }} // Adjusted width
            >
              {companies?.data.map((company: any) => (
                <option key={company.id} value={company.name}>
                  {company.name}
                </option>
              ))}
            </Select>
          )}
        </FormControl>
        <Button type="submit" colorScheme="blue" width={{ base: "100%", md: "30%" }}>
          Submit for Analysis
        </Button>
      </VStack>
    </Box>
  );
}

function InfringementsResult({ data, isLoading }: { data?: any; isLoading: boolean }) {
  const borderColor = useColorModeValue("gray.200", "gray.600");
  const [showFullExplanation, setShowFullExplanation] = useState<{ [key: number]: boolean }>({});

  if (isLoading) {
    return (
      <Box width="100%" mt={4}>
        <Progress size="md" isIndeterminate colorScheme="teal" />
      </Box>
    );
  }

  if (!data) {
    return null;
  }

  const toggleExplanation = (index: number) => {
    setShowFullExplanation((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  return (
    <TableContainer maxWidth="100%" overflowX="auto">
      <Box mt={6} maxWidth="100%" whiteSpace="pre-wrap" wordBreak="break-word">
        <Heading size="md">Overall Risk Assessment</Heading>
        <Box mt={2} p={2} borderWidth="1px" borderRadius="md" borderColor={borderColor} bg={useColorModeValue("gray.50", "gray.800")}>
          {data.overall_risk_assessment}
        </Box>
      </Box>
      <Divider my={4} borderColor={borderColor} />
      <Table
        variant="striped"
        colorScheme="teal"
        size="md"
        border="1px solid"
        borderColor={borderColor}
        width="100%"
      >
        <Thead bg={useColorModeValue("gray.100", "gray.700")}>
          <Tr>
            <Th borderRight="1px solid" borderColor={borderColor} maxWidth="150px" whiteSpace="nowrap">
              Product Name
            </Th>
            <Th borderRight="1px solid" borderColor={borderColor} maxWidth="150px" whiteSpace="nowrap">
              Infringement Likelihood
            </Th>
            <Th borderRight="1px solid" borderColor={borderColor} maxWidth="150px" whiteSpace="nowrap">
              Relevant Claims
            </Th>
            <Th borderRight="1px solid" borderColor={borderColor} maxWidth="300px" whiteSpace="pre-wrap" wordBreak="break-word">
              Explanation
            </Th>
            <Th borderRight="1px solid" borderColor={borderColor} maxWidth="200px" whiteSpace="pre-wrap" wordBreak="break-word">
              Specific Features
            </Th>
            <Th maxWidth="150px" whiteSpace="nowrap">Analysis Date</Th>
          </Tr>
        </Thead>
        <Tbody>
          {data.top_infringing_products.map((product: any, index: number) => (
            <Tr key={index}>
              <Td maxWidth="150px" whiteSpace="nowrap" overflow="hidden" textOverflow="ellipsis">
                {product.product_name}
              </Td>
              <Td maxWidth="150px" whiteSpace="nowrap" overflow="hidden" textOverflow="ellipsis">
                {product.infringement_likelihood}
              </Td>
              <Td maxWidth="150px" whiteSpace="pre-wrap" wordBreak="break-word">
                <ul style={{ paddingLeft: "1rem" }}>
                  {product.relevant_claims.map((claim: string, i: number) => (
                    <li key={i}>{claim}</li>
                  ))}
                </ul>
              </Td>
              <Td maxWidth="300px" whiteSpace="pre-wrap" wordBreak="break-word">
                {showFullExplanation[index]
                  ? product.explanation
                  : `${product.explanation.substring(0, 100)}...`}
                {product.explanation.length > 100 && (
                  <Button
                    variant="link"
                    colorScheme="blue"
                    size="sm"
                    onClick={() => toggleExplanation(index)}
                  >
                    {showFullExplanation[index] ? "Show Less" : "Show More"}
                  </Button>
                )}
              </Td>
              <Td maxWidth="200px" whiteSpace="pre-wrap" wordBreak="break-word">
                <ul style={{ paddingLeft: "1rem" }}>
                  {product.specific_features.map((feature: string, i: number) => (
                    <li key={i}>{feature}</li>
                  ))}
                </ul>
              </Td>
              <Td maxWidth="150px" whiteSpace="nowrap">{new Date(data.analysis_date).toLocaleString()}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
}


function InfringementAnalysis() {
  const [result, setResult] = useState<any>(null);

  const mutation: UseMutationResult<any, Error, { patentId: string; companyName: string }> = useMutation({
    mutationKey: ["checkInfringement"],
    mutationFn: ({ patentId, companyName }: { patentId: string; companyName: string }) =>
      InfringementService.checkInfringement({ patentId, companyName }),
    onSuccess: (data) => {
      setResult(data);
    },
  });

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
      <InfringementsResult data={result} isLoading={mutation.status === "pending"} />
    </Container>
  );
}
