
package com.example;

import java.util.List;
import java.util.ArrayList;

/**
 * A sample test class for demonstration
 */
public class TestClass {
    private String name;
    private List<String> items;
    
    public TestClass(String name) {
        this.name = name;
        this.items = new ArrayList<>();
    }
    
    /**
     * Add an item to the list
     */
    public void addItem(String item) {
        items.add(item);
    }
    
    /**
     * Get all items
     */
    public List<String> getItems() {
        return new ArrayList<>(items);
    }
    
    public String getName() {
        return name;
    }
}
