package myJava;
import java.awt.Point;

public class Main {
    
    public static void main(String[] args){
        
        //set values for attributes this way
        Circle my_circle = new Circle(new Point(2,3), 3.14);
        System.out.println("Center: " + my_circle.Center + ", Radius: " + my_circle.Radius);
        Circle my_circle1 = new Circle(new Point(3,4), 2.13);
        System.out.println("Center: " + my_circle.Center + ", Radius: " + my_circle1.Radius);


        //or this way
        // my_circle.Center = new Point(2,3);
        my_circle.Radius = 3.14;
        
        //or this way
        my_circle.setCenter(new Point(2,3));
        my_circle.setRadius(3.14);


        System.out.println(my_circle.getArea());
        // System.out.println(my_circle.Radius);
        // System.out.println(my_circle.Center);
    }
}
