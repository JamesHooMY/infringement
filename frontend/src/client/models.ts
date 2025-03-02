export type Body_login_login_access_token = {
  grant_type?: string | null
  username: string
  password: string
  scope?: string
  client_id?: string | null
  client_secret?: string | null
}

export type HTTPValidationError = {
  detail?: Array<ValidationError>
}

export type ItemCreate = {
  title: string
  description?: string | null
}

export type ItemPublic = {
  title: string
  description?: string | null
  id: string
  owner_id: string
}

export type ItemUpdate = {
  title?: string | null
  description?: string | null
}

export type ItemsPublic = {
  data: Array<ItemPublic>
  count: number
}

export type Message = {
  message: string
}

export type NewPassword = {
  token: string
  new_password: string
}

export type Token = {
  access_token: string
  token_type?: string
}

export type UpdatePassword = {
  current_password: string
  new_password: string
}

export type UserCreate = {
  email: string
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  password: string
}

export type UserPublic = {
  email: string
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  id: string
}

export type UserRegister = {
  email: string
  password: string
  full_name?: string | null
}

export type UserUpdate = {
  email?: string | null
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  password?: string | null
}

export type UserUpdateMe = {
  full_name?: string | null
  email?: string | null
}

export type UsersPublic = {
  data: Array<UserPublic>
  count: number
}

export type ValidationError = {
  loc: Array<string | number>
  msg: string
  type: string
}

export type InfringementAnalysisPublic = {
  id: string;
  analysis_id: string;
  patent_id: string;
  company_name: string;
  analysis_date: string; // You can use Date if you plan to parse it as a Date object
  top_infringing_products: Array<{
    product_name: string;
    infringement_likelihood: "High" | "Moderate" | "Low"; // String literals for specific values
    relevant_claims: string[];
    explanation: string;
    specific_features: string[];
  }>;
  overall_risk_assessment: string;
};

export type CompanyPublic = {
  id: string;
  name: string;
  products: Array<{
    name: string;
    description: string;
  }>;
};

export type CompaniesPublic = {
  data: Array<CompanyPublic>;
  count: number;
};

export type PatentPublic = {
  id: string;
  publication_number: string; // * this is the patent_id in the InfringementAnalysis type
  title: string;
  ai_summary?: string | null; // Allow optional and nullable
  raw_source_url?: string | null;
  assignee?: string | null;
  inventors: Array<{
    first_name: string;
    last_name: string;
  }>;
  priority_date: string; // Consider `Date` type
  application_date: string; // Consider `Date` type
  grant_date: string; // Consider `Date` type
  abstract: string;
  description: string;
  claims: Array<{
    num: string;
    text: string;
  }>;
  jurisdictions?: string | null;
  classifications?: string | null;
  application_events?: string | null;
  citations?: string | null;
  image_urls?: string | null;
  landscapes?: string | null;
  created_at: string; // Consider `Date` type
  updated_at: string; // Consider `Date` type
  publish_date: string; // Consider `Date` type
  citations_non_patent?: string | null;
  provenance?: string | null;
  attachment_urls?: string | null;
};

export type PatentsPublic = {
  data: Array<PatentPublic>;
  count: number;
};