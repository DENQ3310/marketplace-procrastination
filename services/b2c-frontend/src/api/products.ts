import apiClient from './client';
import type {
  ProductsListParams,
  ProductsListResponse,
  ProductDetail,
  SKUDetail,
  SKUShort,
} from '../types/api';

export const productsApi = {
  // Get products list with filters
  getProductsList: async (params: ProductsListParams): Promise<ProductsListResponse> => {
    const { categoryId, limit = 20, offset = 0, filters = null, sort = 'default', search = '' } = params;
    const queryParams: Record<string, any> = {
      category_id: categoryId,
      limit,
      offset,
      sort,
      search,
    };
    
    // Only add filters if it's not null
    if (filters !== null) {
      queryParams.filters = filters;
    }
    
    const response = await apiClient.get<ProductsListResponse>('/api/v1/products', {
      params: queryParams,
    });
    return response.data;
  },

  // Get product by ID (full detail)
  getProductById: async (productId: string): Promise<ProductDetail> => {
    const response = await apiClient.get<ProductDetail>(`/api/v1/products/${productId}`);
    return response.data;
  },

  // Get product SKUs (short version)
  getProductSkus: async (productId: string): Promise<SKUShort[]> => {
    const response = await apiClient.get<SKUShort[]>(`/api/v1/products/${productId}/skus`);
    return response.data;
  },

  // Get specific SKU (full detail)
  getSku: async (productId: string, skuId: string): Promise<SKUDetail> => {
    const response = await apiClient.get<SKUDetail>(`/api/v1/products/${productId}/skus/${skuId}`);
    return response.data;
  },

  // Get similar products
  getSimilarProducts: async (
    productId: string,
    categoryId: string,
    limit = 8,
    offset = 0
  ): Promise<ProductsListResponse> => {
    const response = await apiClient.get<ProductsListResponse>(`/api/v1/products/${productId}/similar`, {
      params: {
        category: categoryId,
        limit,
        offset,
      },
    });
    return response.data;
  },
};
