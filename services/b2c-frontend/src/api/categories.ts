import apiClient from './client';
import type {
  CategoriesTreeResponse,
  CategoryInfoResponse,
  CategoryFiltersResponse,
  CategoryFacetsResponse,
} from '../types/api';

export const categoriesApi = {
  // Get categories tree
  getCategoriesTree: async (): Promise<CategoriesTreeResponse> => {
    const response = await apiClient.get<CategoriesTreeResponse>('/api/v1/categories');
    return response.data;
  },

  // Get category info by ID
  getCategoryInfo: async (categoryId: string, includeProductCount = false): Promise<CategoryInfoResponse> => {
    const response = await apiClient.get<CategoryInfoResponse>(`/api/v1/categories/${categoryId}`, {
      params: { include_product_count: includeProductCount },
    });
    return response.data;
  },

  // Get category filters
  getCategoryFilters: async (categoryId: string): Promise<CategoryFiltersResponse> => {
    const response = await apiClient.get<CategoryFiltersResponse>(`/api/v1/categories/${categoryId}/filters`);
    return response.data;
  },

  // Get category facets with applied filters
  getCategoryFacets: async (categoryId: string, filters: string | null = null): Promise<CategoryFacetsResponse> => {
    const response = await apiClient.get<CategoryFacetsResponse>(`/api/v1/categories/${categoryId}/facets`, {
      params: { filters },
    });
    return response.data;
  },
};
