import apiClient from './client';
import type {
  Cart,
  AddCartItemResponse,
  UpdateCartItemResponse,
  CartItemResponse,
  ValidateCartResponse,
} from '../types/api';

export const cartApi = {
  // Get cart contents
  getCart: async (): Promise<Cart> => {
    const response = await apiClient.get<Cart>('/api/v1/cart');
    return response.data;
  },

  // Add item to cart
  addCartItem: async (skuId: string, quantity = 1): Promise<AddCartItemResponse> => {
    const response = await apiClient.post<AddCartItemResponse>('/api/v1/cart/items', {
      sku_id: skuId,
      quantity,
    });
    return response.data;
  },

  // Get single cart item
  getCartItem: async (itemId: string): Promise<CartItemResponse> => {
    const response = await apiClient.get<CartItemResponse>(`/api/v1/cart/items/${itemId}`);
    return response.data;
  },

  // Update cart item quantity
  updateCartItem: async (itemId: string, quantity: number): Promise<UpdateCartItemResponse> => {
    const response = await apiClient.put<UpdateCartItemResponse>(`/api/v1/cart/items/${itemId}`, {
      quantity,
    });
    return response.data;
  },

  // Delete cart item
  deleteCartItem: async (itemId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/cart/items/${itemId}`);
  },

  // Clear entire cart
  clearCart: async (): Promise<void> => {
    await apiClient.delete('/api/v1/cart');
  },

  // Validate cart (requires auth)
  validateCart: async (cartItemIds: string[] | null = null): Promise<ValidateCartResponse> => {
    const response = await apiClient.get<ValidateCartResponse>('/cart/validate', {
      params: { cart_item_ids: cartItemIds },
    });
    return response.data;
  },
};
