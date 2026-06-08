import { create } from 'zustand';
import { cartApi } from '../api';
import type { Cart, AddCartItemResponse, UpdateCartItemResponse } from '../types/api';

interface CartStore {
  cart: Cart | null;
  loading: boolean;
  error: string | null;
  fetchCart: () => Promise<void>;
  addItem: (skuId: string, quantity?: number) => Promise<AddCartItemResponse>;
  updateItem: (itemId: string, quantity: number) => Promise<UpdateCartItemResponse>;
  removeItem: (itemId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  getItemCount: () => number;
  getTotalPrice: () => number;
}

const useCartStore = create<CartStore>((set, get) => ({
  cart: null,
  loading: false,
  error: null,

  // Fetch cart from API
  fetchCart: async () => {
    set({ loading: true, error: null });
    try {
      const cart = await cartApi.getCart();
      set({ cart, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },

  // Add item to cart
  addItem: async (skuId: string, quantity = 1) => {
    set({ loading: true, error: null });
    try {
      const result = await cartApi.addCartItem(skuId, quantity);
      set({ cart: result.cart, loading: false });
      return result;
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
      throw error;
    }
  },

  // Update item quantity
  updateItem: async (itemId: string, quantity: number) => {
    set({ loading: true, error: null });
    try {
      const result = await cartApi.updateCartItem(itemId, quantity);
      set({ cart: result.cart, loading: false });
      return result;
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
      throw error;
    }
  },

  // Remove item from cart
  removeItem: async (itemId: string) => {
    set({ loading: true, error: null });
    try {
      await cartApi.deleteCartItem(itemId);
      await get().fetchCart();
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
      throw error;
    }
  },

  // Clear cart
  clearCart: async () => {
    set({ loading: true, error: null });
    try {
      await cartApi.clearCart();
      set({ cart: { items: [], summary: { total_items: 0, total_price: 0 } }, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
      throw error;
    }
  },

  // Get cart item count
  getItemCount: () => {
    const { cart } = get();
    return cart?.summary?.total_items || 0;
  },

  // Get cart total price
  getTotalPrice: () => {
    const { cart } = get();
    return cart?.summary?.total_price || 0;
  },
}));

export default useCartStore;
