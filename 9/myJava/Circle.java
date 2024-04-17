package myJava;
import java.awt.Point;


public class Circle {

    // every object in this class will have the following attributes
    public Point Center;
    public double Radius;

    public Circle(Point Center, Double Radius) {
        this.Center = Center;
        this.Radius = Radius;
    }

    public void setRadius(double newRadius) {
        Radius = newRadius;
    }

    void setCenter(Point newCenter) {
        Center = newCenter;
    }

    double getArea() {
        return (Radius) * (Radius) * 3.14;
    }

    double getPerimeter() {
        return 2 * 3.14 * (Radius);
    }

}
