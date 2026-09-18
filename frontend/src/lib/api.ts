import type {
  AIGeneration,
  AIAnalysis,
  Analytics,
  Campaign,
  CampaignInput,
  CampaignSendResponse,
  LoginResponse,
  Subscriber,
  SubscriberListResponse,
  SubscriberStatus,
  User,
} from "../types";


const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000/api/v1";


export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(
    message: string,
    status: number,
    detail?: unknown,
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}


export function getAccessToken():
  | string
  | null {
  return localStorage.getItem(
    "access_token",
  );
}


export function setAccessToken(
  token: string,
): void {
  localStorage.setItem(
    "access_token",
    token,
  );
}


export function clearAccessToken(): void {
  localStorage.removeItem(
    "access_token",
  );
}


async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token =
    getAccessToken();

  const headers = new Headers(
    options.headers,
  );

  headers.set(
    "Accept",
    "application/json",
  );

  if (options.body) {
    headers.set(
      "Content-Type",
      "application/json",
    );
  }

  if (token) {
    headers.set(
      "Authorization",
      `Bearer ${token}`,
    );
  }

  let response: Response;

  try {
    response = await fetch(
      `${API_URL}${path}`,
      {
        ...options,
        headers,
      },
    );
  } catch {
    throw new ApiError(
      "Unable to connect to SmartMail AI backend.",
      0,
    );
  }

  let data: unknown = null;

  const contentType =
    response.headers.get(
      "content-type",
    );

  if (
    contentType?.includes(
      "application/json",
    )
  ) {
    try {
      data =
        await response.json();
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    let message =
      `Request failed with status ${response.status}.`;

    if (
      typeof data === "object" &&
      data !== null &&
      "detail" in data
    ) {
      const detail =
        (
          data as {
            detail: unknown;
          }
        ).detail;

      if (
        typeof detail === "string"
      ) {
        message = detail;
      } else if (
        Array.isArray(detail)
      ) {
        message =
          detail
            .map(
              (item) =>
                typeof item ===
                  "object" &&
                item !== null &&
                "msg" in item
                  ? String(
                      (
                        item as {
                          msg: unknown;
                        }
                      ).msg,
                    )
                  : String(item),
            )
            .join(", ");
      }
    }

    if (
      response.status === 401
    ) {
      clearAccessToken();

      window.dispatchEvent(
        new Event(
          "smartmail:auth-expired",
        ),
      );
    }

    throw new ApiError(
      message,
      response.status,
      data,
    );
  }

  if (
    response.status === 204
  ) {
    return undefined as T;
  }

  return data as T;
}


/* =========================
   AUTH
========================= */

export function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  return request<LoginResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
      }),
    },
  );
}


export function register(
  name: string,
  email: string,
  password: string,
): Promise<User> {
  return request<User>(
    "/auth/register",
    {
      method: "POST",
      body: JSON.stringify({
        name,
        email,
        password,
      }),
    },
  );
}


/* =========================
   SUBSCRIBERS
========================= */

export function getSubscribers(
  params: {
    page?: number;
    page_size?: number;
    search?: string;
    status?: SubscriberStatus;
  } = {},
): Promise<SubscriberListResponse> {
  const query =
    new URLSearchParams();

  if (params.page) {
    query.set(
      "page",
      String(params.page),
    );
  }

  if (params.page_size) {
    query.set(
      "page_size",
      String(params.page_size),
    );
  }

  if (
    params.search?.trim()
  ) {
    query.set(
      "search",
      params.search.trim(),
    );
  }

  if (params.status) {
    query.set(
      "status",
      params.status,
    );
  }

  const queryString =
    query.toString();

  return request<SubscriberListResponse>(
    `/subscribers${
      queryString
        ? `?${queryString}`
        : ""
    }`,
  );
}


export function createSubscriber(
  name: string,
  email: string,
): Promise<Subscriber> {
  return request<Subscriber>(
    "/subscribers",
    {
      method: "POST",
      body: JSON.stringify({
        name,
        email,
      }),
    },
  );
}


export function updateSubscriber(
  id: number,
  data: Partial<{
    name: string;
    email: string;
    status: SubscriberStatus;
  }>,
): Promise<Subscriber> {
  return request<Subscriber>(
    `/subscribers/${id}`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
  );
}


export function deleteSubscriber(
  id: number,
): Promise<void> {
  return request<void>(
    `/subscribers/${id}`,
    {
      method: "DELETE",
    },
  );
}


/* =========================
   CAMPAIGNS
========================= */

export function getCampaigns(): Promise<
  Campaign[]
> {
  return request<Campaign[]>(
    "/campaigns",
  );
}


export function createCampaign(
  data: CampaignInput,
): Promise<Campaign> {
  return request<Campaign>(
    "/campaigns",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
}


export function updateCampaign(
  id: number,
  data: Partial<CampaignInput>,
): Promise<Campaign> {
  return request<Campaign>(
    `/campaigns/${id}`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
  );
}


export function deleteCampaign(
  id: number,
): Promise<void> {
  return request<void>(
    `/campaigns/${id}`,
    {
      method: "DELETE",
    },
  );
}


export function sendCampaign(
  id: number,
): Promise<CampaignSendResponse> {
  return request<CampaignSendResponse>(
    `/campaigns/${id}/send`,
    {
      method: "POST",
    },
  );
}


export function getCampaignAnalytics(
  id: number,
): Promise<Analytics> {
  return request<Analytics>(
    `/campaigns/${id}/analytics`,
  );
}


/* =========================
   AI
========================= */

export function generateNewsletter(
  data: {
    topic: string;
    audience: string;
    tone:
      | "professional"
      | "friendly"
      | "casual"
      | "educational"
      | "promotional";
    length:
      | "short"
      | "medium"
      | "long";
    key_points: string[];
  },
): Promise<AIGeneration> {
  return request<AIGeneration>(
    "/ai/generate",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
}


export function analyzeCampaign(
  id: number,
): Promise<AIAnalysis> {
  return request<AIAnalysis>(
    `/ai/analyze-campaign/${id}`,
    {
      method: "POST",
    },
  );
}