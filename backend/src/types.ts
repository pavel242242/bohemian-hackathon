/**
 * Meta Ad Library Response Types
 */

export interface AdArchiveAd {
  id: string;
  name: string;
  ad_creative_bodies?: string[];
  ad_delivery_start_date?: string;
  ad_delivery_stop_date?: string;
  ad_snapshot_url?: string;
  advertiser_name?: string;
  advertiser_id?: string;
  currency?: string;
  spend?: {
    lower_bound?: number;
    upper_bound?: number;
  };
  impression_counts?: Array<{
    lower_bound?: number;
    upper_bound?: number;
    percentage?: number;
  }>;
  platform_positions?: string[];
  regions?: Array<{
    name: string;
    percentage?: number;
  }>;
  target_ages?: string[];
  target_gender?: string;
  target_locations?: string[];
  potential_reach?: {
    lower_bound?: number;
    upper_bound?: number;
  };
  created_at?: string;
  updated_at?: string;
}

export interface AdArchiveResponse {
  data: AdArchiveAd[];
  paging?: {
    cursor?: string;
    before?: string;
    after?: string;
  };
  error?: {
    message: string;
    code: number;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface CampaignQueryParams {
  search?: string;
  limit?: number;
  offset?: number;
  after?: string;
}
