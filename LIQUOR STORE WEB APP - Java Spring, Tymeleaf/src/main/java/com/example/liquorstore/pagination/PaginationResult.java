package com.example.liquorstore.pagination;
import java.beans.PropertyDescriptor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.ParameterizedType;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import com.example.liquorstore.model.OrderInfo;
import com.example.liquorstore.model.ProductInfo;
import org.hibernate.ScrollMode;
import org.hibernate.ScrollableResults;
import org.hibernate.query.Query;

public class PaginationResult<E> {

    private int totalRecords;
    private int currentPage;
    private List<E> list;
    private int maxResult;
    private int totalPages;

    private int maxNavigationPage;

    private List<Integer> navigationPages;
    private final Class<E> type;

    // @page: 1, 2, ..
    public PaginationResult(Query<E> query, int page, int maxResult, int maxNavigationPage) {
        //this.type = (Class<E>) ((ParameterizedType) getClass().getGenericSuperclass()).getActualTypeArguments()[0];
        type = null;

        final int pageIndex = page - 1 < 0 ? 0 : page - 1;

        int fromRecordIndex = pageIndex * maxResult;
        int maxRecordIndex = fromRecordIndex + maxResult;

        ScrollableResults resultScroll = query.scroll(ScrollMode.SCROLL_INSENSITIVE);

        List<E> results = new ArrayList<>();

        boolean hasResult = resultScroll.first();

        if (hasResult) {
            // Scroll to position:
            hasResult = resultScroll.scroll(fromRecordIndex);

            if (hasResult) {
                do {
                    E record = (E) resultScroll.get();
                    results.add(record);
                } while (resultScroll.next()//
                        && resultScroll.getRowNumber() >= fromRecordIndex
                        && resultScroll.getRowNumber() < maxRecordIndex);

            }

            // Go to Last record.
            resultScroll.last();
        }

        // Total Records
        this.totalRecords = resultScroll.getRowNumber() + 1;
        this.currentPage = pageIndex + 1;
        this.list = results;
        this.maxResult = maxResult;

        if (this.totalRecords % this.maxResult == 0) {
            this.totalPages = this.totalRecords / this.maxResult;
        } else {
            this.totalPages = (this.totalRecords / this.maxResult) + 1;
        }

        this.maxNavigationPage = maxNavigationPage;

        if (maxNavigationPage < totalPages) {
            this.maxNavigationPage = maxNavigationPage;
        }

        this.calcNavigationPages();
    }

    private void calcNavigationPages() {

        this.navigationPages = new ArrayList<Integer>();

        int current = this.currentPage > this.totalPages ? this.totalPages : this.currentPage;

        int begin = current - this.maxNavigationPage / 2;
        int end = current + this.maxNavigationPage / 2;

        // The first page
        navigationPages.add(1);
        if (begin > 2) {

            // Using for '...'
            navigationPages.add(-1);
        }

        for (int i = begin; i < end; i++) {
            if (i > 1 && i < this.totalPages) {
                navigationPages.add(i);
            }
        }

        if (end < this.totalPages - 2) {

            // Using for '...'
            navigationPages.add(-1);
        }
        // The last page.
        navigationPages.add(this.totalPages);
    }

    public int getTotalPages() {
        return totalPages;
    }

    public int getTotalRecords() {
        return totalRecords;
    }

    public int getCurrentPage() {
        return currentPage;
    }

    public List<E> getList() {
        return list;
    }

    public List<ProductInfo> getProductList() {
        List<ProductInfo> productList = (List<ProductInfo>) list;

        try {
            System.out.println(list.get(0));
            Object someObject = list.get(0);
            for (Field field : someObject.getClass().getDeclaredFields()) {
                field.setAccessible(true); // You might want to set modifier to public first.
                Object value = field.get(someObject);
                System.out.println("da" + field.getName());
                if (value != null) {
                    System.out.println(field.getName() + "=" + value);
                }
            }
        } catch (Exception e) {
            System.out.println("muie");
            return null;
        }

        return null;
    }

    public int getMaxResult() {
        return maxResult;
    }

    public List<Integer> getNavigationPages() {
        return navigationPages;
    }

}
